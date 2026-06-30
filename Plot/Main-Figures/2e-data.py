import os
import gzip
import sys
from collections import Counter

UNHANDLED_OUTPUT = "2e-data.unhandled_samples.tsv"
OUTLIER_OUTPUT = "2e-data.outliers.tsv"
OUTLIER_ID_OUTPUT = "2e-data.outlier_sample_ids.tsv"
VERBOSE = False

def is_vcf(filename):
    return filename.endswith(".vcf") or filename.endswith(".vcf.gz")

def open_vcf(path):
    return gzip.open(path, 'rt') if path.endswith('.gz') else open(path, 'r')

def classify_variant(ref, alt):
    # Structural variants, such as <DEL> and <INS>
    if alt.startswith('<') and alt.endswith('>'):
        return "SV"
    if len(ref) == 1 and len(alt) == 1:
        return "SNP"
    elif len(ref) < len(alt):
        return "Insertion"
    elif len(ref) > len(alt):
        return "Deletion"
    elif len(ref) == len(alt) and len(ref) > 1:
        return "Complex"
    else:
        return None

def sample_alt_indexes(format_field, sample_field, alt_count, unhandled, context):
    format_keys = format_field.split(':')
    sample_values = sample_field.split(':')
    alt_indexes = set()

    if "GT" not in format_keys:
        unhandled.append(context + ["FORMAT_without_GT", format_field, sample_field])
        return alt_indexes

    gt_index = format_keys.index("GT")
    if gt_index >= len(sample_values):
        unhandled.append(context + ["sample_missing_GT_value", format_field, sample_field])
        return alt_indexes

    gt = sample_values[gt_index]
    if gt in (".", ""):
        return alt_indexes

    alleles = gt.replace("|", "/").split("/")
    for allele in alleles:
        if allele in (".", ""):
            continue
        if not allele.isdigit():
            unhandled.append(context + ["non_numeric_GT_allele", format_field, sample_field])
            continue
        allele_number = int(allele)
        if allele_number == 0:
            continue
        if allele_number > alt_count:
            unhandled.append(context + ["GT_allele_exceeds_ALT_count", format_field, sample_field])
            continue
        alt_indexes.add(allele_number)

    return alt_indexes

def count_variants_in_directory(directory):

    # check
    outliers = []
    outliers_ids = []
    unhandled_samples = []

    # Initialize variant-type counters: each variant type has three categories: both, GN_only, and GC_only
    variant_counts = {
        "SNP": {"both": 0, "GN_only": 0, "GC_only": 0},
        "Insertion": {"both": 0, "GN_only": 0, "GC_only": 0},
        "Deletion": {"both": 0, "GN_only": 0, "GC_only": 0},
        "Complex": {"both": 0, "GN_only": 0, "GC_only": 0},
        "SV": {"both": 0, "GN_only": 0, "GC_only": 0}
    }

    for filename in os.listdir(directory):
        if VERBOSE:
            print(f"Processing file: {filename}")
        if not is_vcf(filename):
            continue
        filepath = os.path.join(directory, filename)
        with open_vcf(filepath) as f:
            gn_indices = []  # Column indices for samples starting with GN, based on the full fields
            gc_indices = []  # Column indices for samples starting with GC, based on the full fields
            header_parsed = False

            for line_number, line in enumerate(f, start=1):
                # Parse the header line to get sample names and corresponding column indices
                if line.startswith('#CHROM'):
                    fields = line.strip().split('\t')
                    # VCF standard format: #CHROM POS ID REF ALT QUAL FILTER INFO FORMAT [sample1 sample2 ...]
                    # Samples start from column 10; zero-indexed column 9
                    for col_idx in range(9, len(fields)):
                        sample_name = fields[col_idx]
                        # Extract the sample ID prefix from the full path, either GCF_xxxxx or starting with GN
                        # Example: ./aaaT~~~aaaT_2~~~aaaT_1/GCF_001701365-1464_8_79.fa.bam
                        # Extract: GCF_001701365
                        sample_basename = sample_name.split('/')[-1]  # Get the file name
                        sample_id = sample_basename.split('-')[0]  # Get GCF_xxxxx or GN
                        #print(sample_id)

                        if sample_id.startswith('GN') or sample_id.startswith('_R_GN'):
                            gn_indices.append(col_idx)
                        elif sample_id.startswith('GC') or sample_id.startswith('_R_GC'):
                            gc_indices.append(col_idx)
                        else:
                            outliers_ids.append(sample_id)

                    header_parsed = True
                    continue

                if header_parsed and len(gn_indices) == 0 and len(gc_indices) == 0:
                    print(f"Warning: No GN or GC samples found in file {filename}")
                    sys.exit(0)
                    sys.exit("error message")

                if line.startswith('#'):
                    continue

                # Header information is required before data rows can be processed
                if not header_parsed:
                    print("Error: VCF header not found before data lines.")
                    continue

                fields = line.strip().split('\t')
                ref = fields[3]
                alt_alleles = fields[4].split(',')
                format_field = fields[8] if len(fields) > 8 else ""
                alt_count = len(alt_alleles)
                gn_alt_indexes = set()
                gc_alt_indexes = set()

                # VCF GT uses 0 for REF and 1..N for the ALT alleles in order.
                def collect_alt_indexes(col_idx):
                    if col_idx >= len(fields):
                        return set()
                    context = [filename, str(line_number), fields[1], ref, fields[4], str(col_idx)]
                    return sample_alt_indexes(format_field, fields[col_idx], alt_count, unhandled_samples, context)

                for col_idx in gn_indices:
                    gn_alt_indexes.update(collect_alt_indexes(col_idx))
                for col_idx in gc_indices:
                    gc_alt_indexes.update(collect_alt_indexes(col_idx))

                for alt_index, alt in enumerate(alt_alleles, start=1):
                    vt = classify_variant(ref, alt)
                    if vt is None:
                        unhandled_samples.append([
                            filename, str(line_number), fields[1], ref, fields[4],
                            "ALT_" + str(alt_index), "unclassified_variant", format_field, alt
                        ])
                        continue

                    # Check whether GN and GC samples have this ALT allele
                    gn_has = alt_index in gn_alt_indexes
                    gc_has = alt_index in gc_alt_indexes

                    # Count into the corresponding category
                    if gn_has and gc_has:
                        variant_counts[vt]["both"] += 1
                    elif gn_has:
                        variant_counts[vt]["GN_only"] += 1
                    elif gc_has:
                        variant_counts[vt]["GC_only"] += 1
                    else:
                        outliers.append([filename, fields[1], fields[3], alt])  # Variants appearing in neither GN nor GC are treated as outliers

            if VERBOSE:
                print(len(gn_indices), len(gc_indices))

    if outliers:
        with open(OUTLIER_OUTPUT, "w") as out:
            out.write("file\tpos\tref\talt\n")
            for row in outliers:
                out.write("\t".join(row) + "\n")
        print(f"Outlier variants written to {OUTLIER_OUTPUT}: {len(outliers)}")
    else:
        print("No outlier variants found.")

    if outliers_ids:
        outlier_id_counts = Counter(outliers_ids)
        with open(OUTLIER_ID_OUTPUT, "w") as out:
            out.write("sample_id\tcount\n")
            for sample_id, count in sorted(outlier_id_counts.items()):
                out.write(f"{sample_id}\t{count}\n")
        print(f"Outlier sample IDs written to {OUTLIER_ID_OUTPUT}: {len(outlier_id_counts)}")
    else:
        print("No outlier sample IDs found.")

    if unhandled_samples:
        with open(UNHANDLED_OUTPUT, "w") as out:
            out.write("file\tline\tpos\tref\talt\tcolumn_or_alt\treason\tformat\tsample_value\n")
            for row in unhandled_samples:
                out.write("\t".join(row) + "\n")
        print(f"Unhandled sample/variant values written to {UNHANDLED_OUTPUT}: {len(unhandled_samples)}")
    else:
        print("No unhandled sample/variant values found.")

    return variant_counts

# Change the path to your VCF folder path
vcf_dir = "./Annotated_variants_in_core_genes/"
variant_counts = count_variants_in_directory(vcf_dir)

print("Total variant counts across all VCF files:")
print("\n" + "="*60)
for vtype in ["SNP", "Insertion", "Deletion", "Complex", "SV"]:
    counts = variant_counts[vtype]
    total = counts["both"] + counts["GN_only"] + counts["GC_only"]
    print(f"\n{vtype}:")
    print(f"  Total: {total}")
    print(f"  Both sample groups: {counts['both']}")
    print(f"  GN samples only: {counts['GN_only']}")
    print(f"  GC samples only: {counts['GC_only']}")

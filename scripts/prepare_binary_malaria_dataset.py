"""
Collapses the Roboflow malaria dataset's fine-grained stage classes
(ring/trophozoite/schizont/gametocyte/difficult) into a single "infected"
class, keeping "red blood cell" as its own class.

Why: pipeline.py's parasitemia calculation already treats every stage class
as interchangeable (POSITIVE_KEYWORDS matches ring/troph/schizont/gameto and
sums them into one infected count) — stage-level labels are never used
downstream. But the raw dataset is ~98% "red blood cell" instances, so the
5 stage classes get a handful of examples each (schizont: 3 instances in the
whole validation split) and the detector never learns to recognize them.
Merging them into one "infected" class turns those scattered, individually
unlearnable examples into one class with enough combined data to actually
train on, without touching anything the app depends on.

Run this after downloading the Roboflow dataset and before training. It
rewrites label files in place, so re-run it after every fresh download
(the raw download is unmerged 6-class data each time).
"""
import argparse
import sys
from pathlib import Path

import yaml

RBC_CLASS_NAME = "red blood cell"


def remap_dataset(data_yaml_path: Path) -> None:
    with open(data_yaml_path) as f:
        cfg = yaml.safe_load(f)

    names = cfg["names"]
    if isinstance(names, dict):
        names = [names[i] for i in range(len(names))]

    rbc_indices = [i for i, n in enumerate(names) if n.strip().lower() == RBC_CLASS_NAME]
    if not rbc_indices:
        raise ValueError(
            f"No class named '{RBC_CLASS_NAME}' found in {data_yaml_path} (classes: {names}). "
            "Update RBC_CLASS_NAME if this dataset uses a different label."
        )
    rbc_old_idx = rbc_indices[0]

    # old class index -> new class index (0 = red blood cell, 1 = infected)
    old_to_new = {i: (0 if i == rbc_old_idx else 1) for i in range(len(names))}

    # Roboflow's YOLOv8 export writes train/val/test as "../<split>/images" —
    # relative to wherever Ultralytics' own datasets_dir setting points, not
    # literally relative to data.yaml's directory. The actual split folders
    # always sit directly alongside data.yaml, so look for them there instead
    # of trusting the yaml's path strings.
    root = data_yaml_path.parent
    label_dirs = []
    for split_name in ("train", "valid", "val", "test"):
        labels_dir = root / split_name / "labels"
        if labels_dir.exists() and labels_dir not in label_dirs:
            label_dirs.append(labels_dir)

    total_files = 0
    total_lines = 0
    for labels_dir in label_dirs:
        for txt_path in labels_dir.glob("*.txt"):
            lines = txt_path.read_text().splitlines()
            new_lines = []
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split()
                old_cls = int(parts[0])
                parts[0] = str(old_to_new[old_cls])
                new_lines.append(" ".join(parts))
            txt_path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""))
            total_files += 1
            total_lines += len(new_lines)

    cfg["nc"] = 2
    cfg["names"] = [RBC_CLASS_NAME, "infected"]
    with open(data_yaml_path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(f"Remapped {total_files} label files ({total_lines} boxes) across {len(label_dirs)} splits.")
    print(f"Old classes: {names}")
    print(f"New classes: {cfg['names']} (nc=2)")
    print(f"Updated {data_yaml_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_yaml", type=str, help="Path to the Roboflow dataset's data.yaml")
    args = parser.parse_args()

    path = Path(args.data_yaml)
    if not path.exists():
        print(f"data.yaml not found at {path}", file=sys.stderr)
        sys.exit(1)

    remap_dataset(path)

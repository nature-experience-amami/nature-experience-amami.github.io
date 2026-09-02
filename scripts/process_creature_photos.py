"""
images/creatures/カテゴリ/生き物ID/ にコピーされた未処理写真を、
EXIF撮影日時に基づいてリネーム・リサイズ・透かし追加する。

実行方法: python scripts/process_creature_photos.py
"""
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


IMAGES_DIR = Path("images/creatures")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
IGNORED_DIR_NAMES = {"failed"}
PROCESSED_RE = re.compile(
    r"^(?P<id>.+)_(?P<number>\d{6})_"
    r"(?P<date>\d{8})_(?P<hour>\d{2})$"
)
WATERMARK = "Photo by Nature Experience"
MAX_LONG_SIDE = 2000
WATERMARK_OPACITY = 190


def ensure_failed_dir(species_dir):
    failed_dir = species_dir / "failed"
    failed_dir.mkdir(exist_ok=True)
    return failed_dir


def move_to_failed(source, species_dir):
    try:
        failed_dir = ensure_failed_dir(species_dir)
        destination = failed_dir / source.name
        counter = 1
        while destination.exists():
            destination = failed_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1

        shutil.move(str(source), str(destination))
        return True
    except Exception as error:
        print(f"失敗写真の移動に失敗しました: {source} -> {species_dir / 'failed'} ({error})")
        return False


def is_processed(photo, creature_id):
    match = PROCESSED_RE.fullmatch(photo.stem)
    return bool(match and match.group("id") == creature_id)


def get_next_number(photos, creature_id):
    numbers = [
        int(match.group("number"))
        for photo in photos
        if (match := PROCESSED_RE.fullmatch(photo.stem))
        and match.group("id") == creature_id
    ]
    return max(numbers, default=0) + 1


def get_capture_datetime(image):
    exif = image.getexif()
    for tag in (36867, 36868, 306):
        value = exif.get(tag)
        if value:
            try:
                return datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
            except ValueError:
                continue
    return None


def load_font(size):
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def add_watermark(image):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    size = max(24, round(max(image.size) * 0.017))
    font = load_font(size)
    margin = max(24, round(max(image.size) * 0.018))
    left, top, right, bottom = draw.textbbox((0, 0), WATERMARK, font=font)
    text_width = right - left
    text_height = bottom - top
    x = image.width - text_width - margin
    y = image.height - text_height - margin

    shadow = (0, 0, 0, WATERMARK_OPACITY)
    white = (255, 255, 255, WATERMARK_OPACITY)
    draw.text((x + 2, y + 2), WATERMARK, font=font, fill=shadow)
    draw.text((x, y), WATERMARK, font=font, fill=white)
    return image


def resize_image(image):
    image = ImageOps.exif_transpose(image)
    long_side = max(image.size)
    if long_side > MAX_LONG_SIDE:
        scale = MAX_LONG_SIDE / long_side
        size = (round(image.width * scale), round(image.height * scale))
        image = image.resize(size, Image.Resampling.LANCZOS)
    return image


def process_photo(source, target):
    temp_name = None
    try:
        with Image.open(source) as original:
            capture_datetime = get_capture_datetime(original)
            if capture_datetime is None:
                return "missing-exif", None

            image = add_watermark(resize_image(original))
            image = image.convert("RGB")

        with tempfile.NamedTemporaryFile(
            dir=source.parent, prefix=".processing-", suffix=".jpg", delete=False
        ) as temporary:
            temp_name = Path(temporary.name)
        image.save(temp_name, format="JPEG", quality=92, optimize=True)

        if target.exists():
            temp_name.unlink()
            temp_name = None
            return "error", f"変換先が既に存在します: {target.name}"

        temp_name.replace(target)
        temp_name = None
        source.unlink()
        return "processed", capture_datetime
    except Exception as error:
        if temp_name and temp_name.exists():
            temp_name.unlink()
        return "error", str(error)


def scan():
    processed_count = 0
    skipped_count = 0
    missing_exif_count = 0
    error_count = 0
    errors = []
    missing_exif = []

    if not IMAGES_DIR.is_dir():
        print(f"対象フォルダーがありません: {IMAGES_DIR}")
        return 0

    for category_dir in sorted(path for path in IMAGES_DIR.iterdir() if path.is_dir()):
        for species_dir in sorted(
            path for path in category_dir.iterdir() if path.is_dir() and path.name not in IGNORED_DIR_NAMES
        ):
            creature_id = species_dir.name
            photos = sorted(
                path
                for path in species_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_EXTS
            )
            next_number = get_next_number(photos, creature_id)

            for source in photos:
                if is_processed(source, creature_id):
                    skipped_count += 1
                    continue

                try:
                    with Image.open(source) as image:
                        capture_datetime = get_capture_datetime(image)
                except Exception as error:
                    error_count += 1
                    errors.append(f"{source}: {error}")
                    move_to_failed(source, species_dir)
                    continue
                if capture_datetime is None:
                    missing_exif_count += 1
                    missing_exif.append(str(source))
                    move_to_failed(source, species_dir)
                    continue

                target_name = (
                    f"{creature_id}_{next_number:06d}_"
                    f"{capture_datetime:%Y%m%d}_{capture_datetime:%H}.jpg"
                )
                target = species_dir / target_name
                status, detail = process_photo(source, target)
                if status == "processed":
                    processed_count += 1
                    next_number += 1
                else:
                    error_count += 1
                    errors.append(f"{source}: {detail}")
                    move_to_failed(source, species_dir)

    print(f"処理した写真: {processed_count}枚")
    print(f"処理済みとしてスキップ: {skipped_count}枚")
    print(f"EXIF日時なしでスキップ: {missing_exif_count}枚")
    print(f"エラー: {error_count}枚")
    if missing_exif:
        print("EXIF日時を取得できずスキップ:")
        for path in missing_exif:
            print(f"- {path}")
    if errors:
        print("エラーの詳細:")
        for error in errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(scan())

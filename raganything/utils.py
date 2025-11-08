"""
Utility functions for RAGAnything

Contains helper functions for content separation, text insertion, and other utilities
"""

import base64
from typing import Dict, List, Any, Tuple
from pathlib import Path
from lightrag.utils import logger


def separate_content(
    content_list: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Separate text content and multimodal content

    Args:
        content_list: Content list from MinerU parsing

    Returns:
        (text_content, multimodal_items): Pure text content and multimodal items list
    """
    text_parts = []
    multimodal_items = []

    for item in content_list:
        content_type = item.get("type", "text")

        if content_type == "text":
            # Text content
            text = item.get("text", "")
            if text.strip():
                text_parts.append(text)
        else:
            # Multimodal content (image, table, equation, etc.)
            multimodal_items.append(item)

    # Merge all text content
    text_content = "\n\n".join(text_parts)

    logger.info("Content separation complete:")
    logger.info(f"  - Text content length: {len(text_content)} characters")
    logger.info(f"  - Multimodal items count: {len(multimodal_items)}")

    # Count multimodal types
    modal_types = {}
    for item in multimodal_items:
        modal_type = item.get("type", "unknown")
        modal_types[modal_type] = modal_types.get(modal_type, 0) + 1

    if modal_types:
        logger.info(f"  - Multimodal type distribution: {modal_types}")

    return text_content, multimodal_items


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string

    Args:
        image_path: Path to the image file

    Returns:
        str: Base64 encoded string, empty string if encoding fails
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string
    except Exception as e:
        logger.error(f"Failed to encode image {image_path}: {e}")
        return ""


def validate_image_file(image_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate if a file is a valid image file

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum file size in MB

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        path = Path(image_path)

        logger.debug(f"Validating image path: {image_path}")
        logger.debug(f"Resolved path object: {path}")
        logger.debug(f"Path exists check: {path.exists()}")

        # Check if file exists
        if not path.exists():
            logger.warning(f"Image file not found: {image_path}")
            return False

        # Check file extension
        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
            ".tif",
        ]

        path_lower = str(path).lower()
        has_valid_extension = any(path_lower.endswith(ext) for ext in image_extensions)
        logger.debug(
            f"File extension check - path: {path_lower}, valid: {has_valid_extension}"
        )

        if not has_valid_extension:
            logger.warning(f"File does not appear to be an image: {image_path}")
            return False

        # Check file size
        file_size = path.stat().st_size
        max_size = max_size_mb * 1024 * 1024
        logger.debug(
            f"File size check - size: {file_size} bytes, max: {max_size} bytes"
        )

        if file_size > max_size:
            logger.warning(f"Image file too large ({file_size} bytes): {image_path}")
            return False

        logger.debug(f"Image validation successful: {image_path}")
        return True

    except Exception as e:
        logger.error(f"Error validating image file {image_path}: {e}")
        return False


async def insert_text_content(
    lightrag,
    input: str | list[str],
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    ids: str | list[str] | None = None,
    file_paths: str | list[str] | None = None,
):
    """
    Insert pure text content into LightRAG

    Args:
        lightrag: LightRAG instance
        input: Single document string or list of document strings
        split_by_character: if split_by_character is not None, split the string by character, if chunk longer than
        chunk_token_size, it will be split again by token size.
        split_by_character_only: if split_by_character_only is True, split the string by character only, when
        split_by_character is None, this parameter is ignored.
        ids: single string of the document ID or list of unique document IDs, if not provided, MD5 hash IDs will be generated
        file_paths: single string of the file path or list of file paths, used for citation
    """
    logger.info("Starting text content insertion into LightRAG...")

    # Use LightRAG's insert method with all parameters
    await lightrag.ainsert(
        input=input,
        file_paths=file_paths,
        split_by_character=split_by_character,
        split_by_character_only=split_by_character_only,
        ids=ids,
    )

    logger.info("Text content insertion complete")


def get_processor_for_type(modal_processors: Dict[str, Any], content_type: str):
    """
    Get appropriate processor based on content type

    Args:
        modal_processors: Dictionary of available processors
        content_type: Content type

    Returns:
        Corresponding processor instance
    """
    # Direct mapping to corresponding processor
    if content_type == "image":
        return modal_processors.get("image")
    elif content_type == "table":
        return modal_processors.get("table")
    elif content_type == "equation":
        return modal_processors.get("equation")
    else:
        # For other types, use generic processor
        return modal_processors.get("generic")


def get_processor_supports(proc_type: str) -> List[str]:
    """Get processor supported features"""
    supports_map = {
        "image": [
            "Image content analysis",
            "Visual understanding",
            "Image description generation",
            "Image entity extraction",
        ],
        "table": [
            "Table structure analysis",
            "Data statistics",
            "Trend identification",
            "Table entity extraction",
        ],
        "equation": [
            "Mathematical formula parsing",
            "Variable identification",
            "Formula meaning explanation",
            "Formula entity extraction",
        ],
        "generic": [
            "General content analysis",
            "Structured processing",
            "Entity extraction",
        ],
    }
    return supports_map.get(proc_type, ["Basic processing"])


class ImageDeduplicator:
    """
    Image deduplicator using perceptual hashing

    Uses average hash algorithm to detect duplicate and near-duplicate images.
    Particularly useful for identifying repeated logos, headers, and footers in documents.

    Attributes:
        hash_size: Size of the hash (default 8 = 64 bits)
        similarity_threshold: Maximum Hamming distance to consider images as duplicates
            - 0: Identical images only
            - 1-5: Very similar (logos with slight variations)
            - 6-10: Similar images
            - >10: Different images
        seen_hashes: Dictionary mapping hashes to original image paths
    """

    def __init__(self, hash_size: int = 8, similarity_threshold: int = 5):
        """
        Initialize image deduplicator

        Args:
            hash_size: Size of the perceptual hash (8 = 64 bits recommended)
            similarity_threshold: Hamming distance threshold for duplicates (5 recommended)
        """
        self.hash_size = hash_size
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = {}  # hash_str -> original_path

        logger.info(
            f"ImageDeduplicator initialized: hash_size={hash_size}, "
            f"threshold={similarity_threshold}"
        )

    def get_image_hash(self, image_path: Path) -> str:
        """
        Generate perceptual hash for an image using average hash algorithm

        Args:
            image_path: Path to image file

        Returns:
            Hexadecimal string representation of the hash

        Raises:
            Exception: If image cannot be loaded or hashed
        """
        try:
            from PIL import Image
            import imagehash

            img = Image.open(image_path)
            hash_value = imagehash.average_hash(img, hash_size=self.hash_size)
            return str(hash_value)

        except Exception as e:
            logger.error(f"Failed to hash image {image_path}: {e}")
            raise

    def calculate_hamming_distance(self, hash1: str, hash2: str) -> int:
        """
        Calculate Hamming distance between two hash strings

        Args:
            hash1: First hash string (hex)
            hash2: Second hash string (hex)

        Returns:
            Hamming distance (number of differing bits)
        """
        try:
            # Convert hex strings to integers and XOR them
            xor_result = int(hash1, 16) ^ int(hash2, 16)
            # Count number of 1s in binary representation
            distance = bin(xor_result).count('1')
            return distance
        except Exception as e:
            logger.error(f"Failed to calculate Hamming distance: {e}")
            return 999  # Return large distance on error

    def is_duplicate(self, image_path: Path) -> Tuple[bool, Path | None]:
        """
        Check if image is a duplicate of a previously seen image

        Args:
            image_path: Path to image to check

        Returns:
            Tuple of (is_duplicate, original_path)
            - is_duplicate: True if image is duplicate
            - original_path: Path to original image (None if not duplicate)
        """
        try:
            # Generate hash for current image
            current_hash = self.get_image_hash(image_path)

            # Check against all seen hashes
            for seen_hash, original_path_str in self.seen_hashes.items():
                distance = self.calculate_hamming_distance(current_hash, seen_hash)

                if distance <= self.similarity_threshold:
                    original_path = Path(original_path_str)
                    logger.debug(
                        f"Duplicate found: {image_path.name} matches {original_path.name} "
                        f"(distance={distance})"
                    )
                    return True, original_path

            # Not a duplicate - register this hash
            self.seen_hashes[current_hash] = str(image_path)
            logger.debug(f"New unique image registered: {image_path.name}")
            return False, None

        except Exception as e:
            logger.error(f"Error checking duplicate for {image_path}: {e}")
            # On error, treat as unique to avoid losing data
            return False, None

    def deduplicate_images(
        self,
        image_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Deduplicate a list of images

        Args:
            image_paths: List of image paths to deduplicate

        Returns:
            Dictionary with:
                - 'unique': List of unique image paths
                - 'duplicates': List of (duplicate_path, original_path) tuples
                - 'stats': Statistics dictionary
        """
        unique_images = []
        duplicates = []

        logger.info(f"Starting deduplication of {len(image_paths)} images...")

        for img_path in image_paths:
            is_dup, original = self.is_duplicate(img_path)

            if is_dup:
                duplicates.append((img_path, original))
            else:
                unique_images.append(img_path)

        # Calculate statistics
        total = len(image_paths)
        unique_count = len(unique_images)
        duplicate_count = len(duplicates)
        reduction_pct = (duplicate_count / total * 100) if total > 0 else 0

        stats = {
            'total': total,
            'unique': unique_count,
            'duplicates': duplicate_count,
            'reduction_percentage': reduction_pct
        }

        logger.info(
            f"Deduplication complete: {total} total, {unique_count} unique, "
            f"{duplicate_count} duplicates ({reduction_pct:.1f}% reduction)"
        )

        return {
            'unique': unique_images,
            'duplicates': duplicates,
            'stats': stats
        }

    def reset(self):
        """Reset the deduplicator by clearing seen hashes"""
        self.seen_hashes.clear()
        logger.info("Deduplicator reset - all hashes cleared")

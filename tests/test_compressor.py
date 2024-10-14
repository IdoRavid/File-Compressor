from pathlib import Path
from typing import Union
from filecmp import cmp
import pytest

# Import necessary classes and constants from the compressor module
from compressor import RLE_Compressor, LZW_Compressor, Compressor, TEST_BASE_PATH
from encoded_file import Encoded_File

# Define the base path for compressor tests
COMPRESSOR_BASE_PATH = TEST_BASE_PATH / "compressor tests"

# Define fixtures for RLE and LZW compressors
@pytest.fixture
def rle_compressor() -> RLE_Compressor:
    return RLE_Compressor()

@pytest.fixture()
def lzw_compressor() -> LZW_Compressor:
    return LZW_Compressor()

# Test string encoding and decoding for both RLE and LZW compressors
def test_string_encode_decode(lzw_compressor, rle_compressor):
    string_encode_and_decode(rle_compressor)
    string_encode_and_decode(lzw_compressor)

# Helper function for encoding and decoding strings
def string_encode_and_decode(compressor: Compressor) -> None:
    # Test various string inputs and byte sizes
    assert_encode_and_decode(compressor, 9 * "a", 5)
    assert_encode_and_decode(compressor, 10 * "a", 5)
    assert_encode_and_decode(compressor, 100 * "a", 5)

    # Test longer texts
    text: str = (
        "Boy desirous families prepared gay reserved add ecstatic say. Replied joy age visitor nothing cottage. "
        "Mrs door paid led loud sure easy read. Hastily at perhaps as neither or ye fertile tedious visitor. Use "
        "fine bed none call busy dull when. Quiet ought match my right by table means. Principles up do in me "
        "favourable")
    assert_encode_and_decode(compressor, text, 6)
    # Test larger byte size changes
    assert_encode_and_decode(compressor, 10 * "a", 11)

    # Test single character
    assert_encode_and_decode(compressor, "a", 5)

    # Test repeated characters
    assert_encode_and_decode(compressor, "aaaabbbcc", 5)

    # Test mixed characters
    assert_encode_and_decode(compressor, "abCDE@#$", 5)

    # Test special characters
    assert_encode_and_decode(compressor, "!@#$%^&*()_+{}[]|;:,.<>?/~`", 5)

    # Test newline characters
    assert_encode_and_decode(compressor, "Hello\nWorld", 5)

    # Test whitespace characters
    assert_encode_and_decode(compressor, "   \t\t\n", 5)

    # Test mixed content
    mixed_content = "abc123!@#"
    assert_encode_and_decode(compressor, mixed_content, 5)

    # Test edge lengths
    edge_lengths = "abcde"
    assert_encode_and_decode(compressor, edge_lengths, 1)
    assert_encode_and_decode(compressor, edge_lengths, 1000)

    # Test long runs
    long_run = "a" * 10000 + "b" * 10000 + "c" * 10000
    assert_encode_and_decode(compressor, long_run, 5)

    # Test non-positive length
    with pytest.raises(ValueError):
        compressor.encode(10 * "a", "path", 0)
    with pytest.raises(ValueError):
        compressor.encode(10 * "a", "path", -1)
    with pytest.raises(ValueError):
        compressor.encode(10 * "a", "path", 0)
    with pytest.raises(ValueError):
        assert_encode_and_decode(compressor, "", 5)

    # Test wrong types
    with pytest.raises(TypeError):
        compressor.encode(10, 0)
    with pytest.raises(TypeError):
        compressor.encode(Exception, 0)
    with pytest.raises(ValueError):
        compressor.encode("text", "path", 0)
    with pytest.raises(TypeError):
        compressor.encode("text", "path", "text")
    with pytest.raises(TypeError):
        compressor.encode("text", 10, 10)

# Test RLE compressor byte length
def test_rle_compressor_byte_length(rle_compressor):
    assert_encode_and_decode(rle_compressor, "strings", 100)
    assert_encode_and_decode(rle_compressor, " kjhjkjhghjkjhghkjcvjkgfgbnbvgfytujknbvcfghjbv", 1)
    assert_encode_and_decode(rle_compressor, b"sddfgfdfgfggffdcvcvijjjjjjjjj", 12)

# Test binary encoding and decoding for both RLE and LZW compressors
def test_binary_encode_decode(lzw_compressor, rle_compressor):
    binary_encode_and_decode(rle_compressor)
    binary_encode_and_decode(lzw_compressor)

# Helper function for encoding and decoding binary data
def binary_encode_and_decode(compressor: Compressor) -> None:
    # Test binary encoding and decoding
    assert_encode_and_decode(compressor, b'some string', 5)
    assert_encode_and_decode(compressor, b'a longer string than that', 5)
    assert_encode_and_decode(compressor, b'string looooooooooooooooooooong', 5)

    # Test binary string
    other_text = b'asas'
    assert_encode_and_decode(compressor, other_text, 9)

# Helper function to assert encoding and decoding results
def assert_encode_and_decode(compressor: Compressor, text: Union[str, bytes], length: int) -> None:
    encoded_file = compressor.encode(text, "some_path", length, 99)
    new_text = compressor.decode(encoded_file)
    assert text == new_text
    assert new_text is not False

# Test encoding and decoding of text files
def text_file_encode_decode(compressor: Compressor):
    file_path = Path(COMPRESSOR_BASE_PATH / "text_file.txt")
    temp_path = Path(COMPRESSOR_BASE_PATH / "temp_file.txt")
    save_path = Path(COMPRESSOR_BASE_PATH / "new_text.txt")
    if save_path.exists():
        save_path.unlink()
    with open(file_path, 'r') as file:
        file_content = ''
        for line in file.readlines():
            file_content += line
    with open(temp_path, 'w') as temp_file:
        temp_file.write(file_content)
        encoded_file = compressor.encode(file_content, file_path.name, 5, 99)
        decoded_file = compressor.decode(encoded_file)
    with open(save_path, 'w') as new_file:
        new_file.write(decoded_file)
    assert cmp(temp_path, save_path)

# Test encoding and decoding of text files
def test_text_file_encode_decode(rle_compressor, lzw_compressor):
    text_file_encode_decode(rle_compressor)
    text_file_encode_decode(lzw_compressor)

# Test encoding and decoding of binary files
def bin_file_encode_decode(compressor: Compressor):
    file_path = Path(COMPRESSOR_BASE_PATH / "bin_file.xlsx")
    save_path = Path(COMPRESSOR_BASE_PATH / "new_bin_file.xlsx")
    if save_path.exists():
        save_path.unlink()
    with open(file_path, 'rb') as file:
        file_content = file.read()
        encoded_file = compressor.encode(file_content, file_path.name, 10, 99)
        decoded_file = compressor.decode(encoded_file)
    with open(save_path, 'wb') as new_file:
        new_file.write(decoded_file)
    assert cmp(file_path, save_path)

# Test encoding and decoding of binary files
def test_bin_file_encode_decode(rle_compressor, lzw_compressor):
    bin_file_encode_decode(rle_compressor)
    bin_file_encode_decode(lzw_compressor)

# Test RLE string encoding
def test_rle_string_encode(rle_compressor):
    text = "aaa111"
    byte_size = 5
    cap_size = 99
    encoded_file = rle_compressor.encode(text, "path", byte_size, cap_size)
    assert isinstance(encoded_file, Encoded_File)
    assert encoded_file.get_data() == b"01aaa11011"

    another_text = "a new text line which we could use to check"
    byte_size_new = 3
    encoded_file = rle_compressor.encode(another_text, "Path", byte_size_new, 99)
    assert encoded_file.get_data() == b"01a n01ew 01tex01t l01ine01 wh01ich01 we01 co01uld01 us01e t01o c01hec01k"

# Test RLE string decoding
def test_rle_string_decode(rle_compressor):
    encoded = b"01aaa11011"
    encoded_file = Encoded_File(b"01aaa11011", False, 5, Path("path"), "RLE", 99)
    decoded = rle_compressor.decode(encoded_file)
    assert "aaa111" == decoded

    new_encoded_file = Encoded_File(b"01a n01ew 01tex01t l01ine01 wh01ich01 we01 co01uld01 us01e t01o c01hec01k", False,
                                    3, Path("path"), "RLE", 99)
    decoded = rle_compressor.decode(new_encoded_file)
    assert "a new text line which we could use to check" == decoded

# Test RLE binary encoding
def test_rle_binary_encode(rle_compressor):
    some_string = "111222333"
    text = some_string.encode('utf-8')
    byte_size = 3
    encoded_file = rle_compressor.encode(text, "path", byte_size, 99)
    assert isinstance(encoded_file, Encoded_File)
    assert encoded_file.get_data() == b"\x30\x31\x31\x31\x31\x30\x31\x32\x32\x32\x30\x31\x33\x33\x33"

# Test invalid input for encoding
def invalid_input(compressor: Compressor):
    # Test encoding with invalid input type
    with pytest.raises(TypeError):
        compressor.encode(123, "path", 5)

    # Test encoding with invalid byte size
    with pytest.raises(ValueError):
        compressor.encode("abc", "path", 0)

    with pytest.raises(ValueError):
        compressor.encode("abc", "path", -5)

# Test invalid input for encoding
def test_invalid_input(rle_compressor, lzw_compressor):
    invalid_input(rle_compressor)
    invalid_input(lzw_compressor)

# Test mixed content encoding and decoding
def test_mixed_content(rle_compressor):
    mixed_content = "aaa111"
    assert_encode_and_decode(rle_compressor, mixed_content, 5)

# Test binary LZW encoding and decoding
def test_binary_lzw(lzw_compressor):
    string = b'123123123'
    encoded = lzw_compressor.binary_encode(string, 5, "name")
    decoded = lzw_compressor.binary_decode(encoded)
    assert string == decoded

# Test general use cases
def test_general_use(rle_compressor, lzw_compressor):
    assert_encode_and_decode(rle_compressor, 100 * "a", 11)
    assert_encode_and_decode(lzw_compressor, 100 * "a", 11)

# Entry point for running tests if the script is executed directly
if __name__ == "__main__":
    pytest.main([__file__])

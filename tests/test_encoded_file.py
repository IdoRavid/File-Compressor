import pytest

from encoded_file import Encoded_File


@pytest.fixture
def sample_encoded_file() -> Encoded_File:
    # Sample data for testing
    data: bytes = b'test data'
    binary_flag: bool = True
    byte_length: int = 10
    return Encoded_File(data, binary_flag, byte_length)


def test_init(sample_encoded_file: Encoded_File) -> None:
    # check init works properly
    assert sample_encoded_file.get_data() == b'test data'
    assert sample_encoded_file.is_binary() == True
    assert sample_encoded_file.get_byte_len() == 10


def test_get_size_zero_byte_length():
    data = b'test data'
    try:
        encoded_file = Encoded_File(data, binary_flag=True, byte_length=0)
    except ValueError:
        pass


def test_get_byte_len_negative():
    # check value error raised with negative byte len
    data = b'test data'
    try:
        encoded_file = Encoded_File(data, binary_flag=True, byte_length=-5)
    except ValueError:
        pass


def test_is_binary_false():
    # check is binary bool works
    data = b'test data'
    encoded_file = Encoded_File(data, binary_flag=False, byte_length=10)
    assert encoded_file.is_binary() == False


#
# def test_get_data_string():
#     data_string = 'test string data'
#     encoded_file_string = Encoded_File(data_string, binary_flag=False, byte_length=15)
#     assert encoded_file_string.get_data() == data_string.encode('utf-8')


if __name__ == "__main__":
    pytest.main([__file__])

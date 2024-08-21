import pytest
from main import (
    validate_input,
    InvalidInputError,
    InputTooLongError,
    Unsupportedcharacterserror,
)


def test_validate_empty_input():
    with pytest.raises(InvalidInputError) as e:
        validate_input("")

    assert str(e.value) == "Input cannot be empty. Please provide a concept to check"


@pytest.mark.parametrize(
    ("input, expected"),
    (
        ("A normal test input", "a normal test input"),
        ("TEST INPUT ALL CAPS", "test input all caps"),
        ("  MixeD TesT INPUT  ", "mixed test input"),
    ),
)
def test_validate_input(input, expected):
    assert validate_input(input) == expected


def test_validate_input_too_long():
    with pytest.raises(InputTooLongError) as e:
        validate_input(
            "This is a very long test input that exceeds the acceptable length \
                 and should raise an InputTooLongError "
        )
    assert str(e.value) == "Text input too long. Consider shortening."

import pytest
from litelookup.main import (
    validate_input,
    InvalidInputError,
    InputTooLongError,
    UnsupportedCharactersError,
)


def test_validate_empty_input():
    with pytest.raises(InvalidInputError) as e:
        validate_input("", False)

    assert str(e.value) == "Input cannot be empty. Please provide a concept to check"


@pytest.mark.parametrize(
    "input, expected",
    (
        ("A normal test input", "a normal test input"),
        ("TEST INPUT ALL CAPS", "TEST INPUT ALL CAPS"),
        ("  MixeD TesT INPUT  ", "mixed test input"),
        ("Sample-input with one hyphen ", "sample-input with one hyphen"),
    ),
)
def test_validate_input(input, expected):
    print(validate_input(input, False))
    assert validate_input(input, False) == expected


def test_validate_input_too_long():
    with pytest.raises(InputTooLongError) as e:
        validate_input(
            "This is a very long test input that exceeds the acceptable \
                length and should raise an InputTooLongError ",
            False,
        )
    assert str(e.value) == "Text input too long. Consider shortening."


def test_validate_unsupported_input_chars():
    with pytest.raises(UnsupportedCharactersError) as e:
        validate_input('"__This is @ test with unupported chars like & and >",', False)

    assert (
        str(e.value)
        == "Input contains unsupported characters. Please use only letters, numbers, spaces, hyphens, and basic punctuation."
    )


def test_validate_input_contains_only_one_hyphen():
    with pytest.raises(UnsupportedCharactersError) as e:
        validate_input("input with double -- or more --- hyphens together", False)

    assert str(e.value) == "Text cannot contain two or more hyphens together."

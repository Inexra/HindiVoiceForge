from app import split_text


def test_empty_text():
    assert split_text("") == []
    assert split_text("   ") == []


def test_keeps_all_words():
    text = "पहला वाक्य।\n\nदूसरा वाक्य। तीसरा वाक्य!"
    chunks = split_text(text)
    assert " ".join(chunks).replace("।", "।") == "पहला वाक्य। दूसरा वाक्य। तीसरा वाक्य!"


def test_respects_chunk_limit():
    text = ("यह एक लंबा वाक्य है " * 500).strip()
    chunks = split_text(text, max_chars=100)
    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_does_not_drop_long_unbroken_text():
    text = "क" * 250
    chunks = split_text(text, max_chars=50)
    assert "".join(chunks) == text

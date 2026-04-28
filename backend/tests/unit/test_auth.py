from app.core.auth import hash_password, verify_password


class TestHashPassword:
    def test_returns_different_string(self):
        hashed = hash_password("testpassword")
        assert hashed != "testpassword"

    def test_produces_unique_hashes(self):
        """Argon2 uses a random salt, so hashing the same input twice gives different outputs."""
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2

    def test_returns_string(self):
        assert isinstance(hash_password("testpassword"), str)


class TestVerifyPassword:
    def test_correct_password(self):
        hashed = hash_password("mysecretpw")
        assert verify_password("mysecretpw", hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("mysecretpw")
        assert verify_password("wrongpassword", hashed) is False

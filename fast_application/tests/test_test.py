from core.config import settings
import pytest
@pytest.mark.anyio
def test_te():
    print("*"*50)
    print(settings.run.debug)
    assert 5 == 5
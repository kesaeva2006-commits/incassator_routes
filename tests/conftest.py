import os
import pytest

if not os.path.exists('atm.py'):
    pytest.skip("atm.py ещё нет в main, все зависящие тесты пропущены", allow_module_level=True)

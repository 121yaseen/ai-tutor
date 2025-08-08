# save_test_result_to_json
import pytest


@pytest.mark.unit
class TestJsonPush:
    @pytest.mark.asyncio
    def test_json_push(self):
        mock_service = Mock()
        mock_service.

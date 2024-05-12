from flask import jsonify, Response


class Result:

    @staticmethod
    def get_jsonify(success: bool, data: any = None, msg: str = None) -> Response:
        return jsonify({
            'success': success,
            'msg': msg,
            'data': data
        })

    @staticmethod
    def success(data=None, msg: str = "成功", code: int = 200) -> tuple[Response, int]:
        return Result.get_jsonify(True, data, msg), code

    @staticmethod
    def error(msg: str = "失败", code: int = 400) -> tuple[Response, int]:
        return Result.get_jsonify(False, None, msg), code
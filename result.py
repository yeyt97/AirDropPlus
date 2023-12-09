from flask import jsonify


class Result:

    @staticmethod
    def jsonify(success: bool, data=None, msg: str = None):
        return jsonify({
            'success': success,
            'msg': msg,
            'data': data
        })

    @staticmethod
    def success(data=None, msg: str = "成功", code: int = 200):
        return Result.jsonify(True, data, msg), code

    @staticmethod
    def error(msg: str = "失败", code: int = 400):
        return Result.jsonify(False, None, msg), code
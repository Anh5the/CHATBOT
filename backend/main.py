from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order,
        'delete_order_intent': delete_order_intent,
        'order.complete - context: ongoing-remove': complete_order_ongoing_remove_intent,
        'order.delete - context: ongoing-remove': delete_order_intent  # Thêm intent xóa đơn hàng vào đây
    }

    return intent_handler_dict[intent](parameters, session_id)

def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "Đang xử lý")

    return next_order_id

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "Xin lỗi, tôi không thể tìm thấy đơn hàng của bạn. Bạn có thể đặt đơn hàng mới không?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Xin lỗi, tôi không thể xử lý đơn hàng của bạn do lỗi ở phía máy chủ. " \
                               "Vui lòng đặt đơn hàng mới lần nữa."
        else:
            order_total = db_helper.get_total_order_price(order_id)

            fulfillment_text = f"Xuất sắc. Chúng tôi đã đặt đơn hàng của bạn. " \
                           f"Đây là mã đơn hàng của bạn # {order_id}. " \
                           f"Tổng giá trị đơn hàng của bạn là {order_total} và bạn có thể thanh toán khi nhận hàng!"

        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Xin lỗi, tôi không hiểu. Bạn có thể chỉ rõ các món ăn và số lượng không?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"Cho đến nay, bạn đã chọn: {order_str}. Bạn cần thêm gì nữa không?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "Xin lỗi, tôi gặp khó khăn khi tìm đơn hàng của bạn. Bạn có thể đặt đơn hàng mới không?"
        })

    food_items = parameters["food-item"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Đã xóa {",".join(removed_items)} khỏi đơn hàng của bạn!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Đơn hàng hiện tại của bạn không có {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Đơn hàng của bạn đang trống!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Đây là những gì còn lại trong đơn hàng của bạn: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"Tình trạng đơn hàng với mã đơn hàng: {order_id} là: {order_status}"
    else:
        fulfillment_text = f"Không tìm thấy đơn hàng với mã đơn hàng: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def delete_order_intent(parameters, session_id):
    try:
        # Lấy ID đơn hàng từ người dùng
        order_id = parameters['order_id']

        # Kiểm tra xem đơn hàng có tồn tại không
        order_exists = db_helper.check_order_exists(order_id)

        if order_exists:
            # Xoá đơn hàng mà không cần xác nhận
            result = db_helper.delete_order(order_id)

            if result == 1:
                fulfillment_text = f"Đơn hàng #{order_id} đã được xoá."
            else:
                fulfillment_text = f"Xảy ra lỗi khi xoá đơn hàng #{order_id}. Vui lòng thử lại sau."
        else:
            fulfillment_text = f"Không tìm thấy đơn hàng #{order_id}. Bạn có thể nhập lại ID khác?"

        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })

    except KeyError:
        return JSONResponse(content={
            "fulfillmentText": "Xin lỗi, tôi không thể xác định ID đơn hàng cần xoá. Vui lòng thử lại."
        })



def delete_order_confirm_intent(parameters, session_id):
    try:
        order_id = parameters['order_id']

        # Thực hiện việc xác định xem người dùng đã xác nhận huỷ đơn hàng hay không
        # Dựa trên context từ Dialogflow
        context = parameters['outputContexts'][0]['name']  # Giả sử thông tin context được lấy từ payload của Dialogflow

        if 'order.complete - context: ongoing-remove' in context:
            fulfillment_text = f"Đơn hàng #{order_id} đã được xác nhận xóa."
            result = db_helper.delete_order(order_id)

            if result == 1:
                return JSONResponse(content={
                    "fulfillmentText": fulfillment_text
                })
            else:
                fulfillment_text = f"Xảy ra lỗi khi xác nhận xóa đơn hàng #{order_id}. Vui lòng thử lại sau."
                return JSONResponse(content={
                    "fulfillmentText": fulfillment_text
                })
        else:
            return JSONResponse(content={
                "fulfillmentText": f"Đơn hàng #{order_id} không được xóa."
            })

    except KeyError:
        return JSONResponse(content={
            "fulfillmentText": "Xin lỗi, tôi không thể xác định thông tin cần thiết. Vui lòng thử lại."
        })


def complete_order_ongoing_remove_intent(parameters, session_id):
    try:
        order_id = parameters['order_id']
        # Thực hiện các thao tác cần thiết dựa trên logic của bạn
        # Ví dụ: xác nhận hoàn thành đơn hàng và xóa khỏi danh sách đơn hàng đang xử lý
        # Thực hiện các thao tác cần thiết ở đây
        fulfillment_text = f"Đơn hàng #{order_id} đã hoàn thành và xóa khỏi danh sách đang xử lý."
        complete_order(order_id)
        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
    except KeyError:
        return JSONResponse(content={
            "fulfillmentText": "Xin lỗi, không thể xác định thông tin cần thiết. Vui lòng thử lại."
        })


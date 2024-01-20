
import mysql.connector
global cnx

import pymysql

# Thực hiện kết nối đến cơ sở dữ liệu
cnx = pymysql.connect(user='root', password='Anh2142003@', host='localhost', database='chatbotnhom5')


# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()

        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        cnx.commit()

        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()

        return -1

# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    cnx.commit()

    cursor.close()

def get_total_order_price(order_id):
    cursor = cnx.cursor()

    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    return result

# Function to get the next available order_id
def get_next_order_id():
    cursor = cnx.cursor()

    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    if result is None:
        return 1
    else:
        return result + 1

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    cursor = cnx.cursor()

    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()

    if result:
        return result[0]
    else:
        return None

if __name__ == "__main__":
    print(get_next_order_id())

def check_order_exists(order_id):
    cursor = cnx.cursor()
    try:
        query = f"SELECT * FROM orders WHERE order_id = {order_id}"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    except pymysql.Error as err:
        print(f"Lỗi khi kiểm tra đơn hàng: {err}")
        return False
    finally:
        cursor.close()

def delete_order(order_id):
    try:
        cursor = cnx.cursor()

        # Thực hiện truy vấn SQL để xoá đơn hàng từ bảng orders
        delete_query = "DELETE FROM orders WHERE order_id = %s"
        cursor.execute(delete_query, (order_id,))

        # Commit thay đổi
        cnx.commit()

        # Đóng con trỏ
        cursor.close()

        print(f"Đơn hàng #{order_id} đã được xóa thành công!")
        return 1

    except pymysql.Error as err:
        print(f"Lỗi khi xóa đơn hàng: {err}")
        # Rollback nếu cần
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        # Rollback nếu cần
        cnx.rollback()
        return -1

def complete_order(order_id):
    try:
        cursor = cnx.cursor()

        # Thực hiện truy vấn SQL hoàn thành đơn hàng trong cơ sở dữ liệu
        # Ví dụ: cập nhật trạng thái đơn hàng thành hoàn thành
        update_query = "UPDATE orders SET status = 'Completed' WHERE order_id = %s"
        cursor.execute(update_query, (order_id,))

        # Commit thay đổi
        cnx.commit()

        # Đóng con trỏ
        cursor.close()

        print(f"Đơn hàng #{order_id} đã hoàn thành!")
        return 1

    except pymysql.Error as err:
        print(f"Lỗi khi hoàn thành đơn hàng: {err}")
        # Rollback nếu cần
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        # Rollback nếu cần
        cnx.rollback()
        return -1

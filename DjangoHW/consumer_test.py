import json
from channels.generic.websocket import AsyncWebsocketConsumer

class IMDemoConsumer(AsyncWebsocketConsumer):
    # 当客户端尝试建立 WebSocket 连接时调用
    async def connect(self) -> None:
        # 从查询字符串中提取用户名
        self.username: str = self.scope['query_string'].decode('utf-8').split('=')[1]

        # 将当前 WebSocket 连接添加到一个全体用户组中
        # 这样可以确保发给这个组的所有消息都会被转发给目前连接的所有客户端
        await self.channel_layer.group_add(self.username, self.channel_name)

        # 接受 WebSocket 连接
        await self.accept()

    # 当 WebSocket 连接关闭时调用
    async def disconnect(self, close_code: int) -> None:
        # 将当前 WebSocket 从其所在的组中移除
        await self.channel_layer.group_discard(self.username, self.channel_name)

    # 向指定用户组发送 notification
    async def notify(self, event) -> None:
        await self.send(text_data=json.dumps({'type': 'notify'}))





        import json
from channels.generic.websocket import AsyncWebsocketConsumer

class IMDemoConsumer(AsyncWebsocketConsumer):
    async def connect(self):await self.accept()
    async def disconnect(self, close_code):
        # 遍历用户加入的所有聊天室，并从中移除用户
        for room in self.rooms:
            await self.channel_layer.group_discard(
                f'chat_{room.id}',
                self.channel_name
            )

    async def receive(self, text_data):        
        # 解析接收到的消息
        data = json.loads(text_data)
        room_id = data['room_id']
        message_type = data['type']

        # 通过调度方法处理不同类型的消息
        await self.dispatch_message(room, message_type, data)

    async def dispatch_message(self, room, type, data):
        # 根据不同的消息类型执行不同的操作
        if type == "send_message":
            await self.handle_send_message(room, data)
        elif type == "get_history_messages":
            await self.handle_history_messages(room, data)
        elif type == "get_reply_msg_count":
            await self.handle_get_reply_msg_count(room, data['msg_id'])
        elif type == "delete_message":
            await self.handle_delete_message(data['msg_id'])
        elif type == "judge_id_read":
            await self.handle_judge_id_read(room, data)
        elif type == "get_reply_message":
            await self.handle_get_reply_message(room, data)
        elif type == "set_read_index":
            await self.set_read_index(room.id, data['read_index'])
            await self.send(json.dumps({"set read index success":data['read_index']}))

    async def handle_send_message(self, room, data):

        message_content = data['message']
        sender_id = self.user.id
        message_payload = await self.save_message_content(message_content, room.id, sender_id, reply_id)
        await self.channel_layer.group_send(f'chat_{room.id}', message_payload)

    async def chat_message(self, event):
        # 将消息发送给WebSocket客户端
        event['type'] = 'chat_message'
        event['ack_id'] = self.message_counter
        self.message_counter += 1
        await self.send('textdata' = event)
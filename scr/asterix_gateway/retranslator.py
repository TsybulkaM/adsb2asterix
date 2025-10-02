import asyncio
from sbs import filter_by_aircraft_state

# --- Настройки ---
REMOTE_HOST = 'data.adsbhub.org'
REMOTE_PORT = 5002

LOCAL_HOST = '0.0.0.0'
LOCAL_PORT = 5002
# ----------------

async def process_and_forward(reader, writer):
    buffer = b''
    try:
        while not reader.at_eof():
            data_chunk = await reader.read(2048)
            if not data_chunk:
                break
            
            buffer += data_chunk
            last_newline = buffer.rfind(b'\n')
            
            if last_newline != -1:
                lines_to_process = buffer[:last_newline + 1]
                buffer = buffer[last_newline + 1:]

                for line_bytes in lines_to_process.split(b'\n'):
                    if not line_bytes:
                        continue
                    
                    sbs_line_str = line_bytes.decode('utf-8')
                    
                    if filter_by_aircraft_state(sbs_line_str):
                        # Условие пройдено, отправляем пакет
                        writer.write(line_bytes + b'\n')
                
                # Важно! После обработки блока строк нужно дождаться их физической отправки
                await writer.drain()
    finally:
        writer.close()

async def handle_client(local_reader, local_writer):
    client_addr = local_writer.get_extra_info('peername')
    print(f"[+] Локальный клиент подключился: {client_addr}")

    try:
        remote_reader, remote_writer = await asyncio.open_connection(REMOTE_HOST, REMOTE_PORT)
        print(f"[+] Установлено соединение с удаленным сервером")
    except Exception as e:
        print(f"[!] Не удалось подключиться к удаленному серверу: {e}")
        local_writer.close()
        return

    # Запускаем пересылку с фильтрацией
    try:
        await process_and_forward(remote_reader, local_writer)
    finally:
        print(f"[-] Сессия для {client_addr} завершена.")
        remote_writer.close()
        local_writer.close()

async def main():
    server = await asyncio.start_server(handle_client, LOCAL_HOST, LOCAL_PORT)
    addr = server.sockets[0].getsockname()
    print(f'Прокси-сервер с фильтром запущен на {addr}')
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
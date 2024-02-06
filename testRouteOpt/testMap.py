import requests

def get_longdo_map(api_key, query):
    base_url = 'https://api.longdo.com/map/services/'
    endpoint = 'geocode'
    
    # สร้าง URL สำหรับเรียกใช้งาน Longdo Map API
    url = f'{base_url}{endpoint}?key={api_key}&q={query}'

    try:
        # ทำ HTTP GET request ไปยัง Longdo Map API
        response = requests.get(url)
        data = response.json()

        # ตรวจสอบว่า request สำเร็จหรือไม่
        if response.status_code == 200:
            return data
        else:
            print(f'Error: {data["status"]} - {data["message"]}')
            return None

    except Exception as e:
        print(f'Error: {e}')
        return None

# แทนค่าด้วย API key ที่คุณได้รับจาก Longdo
api_key = '17d4b8eeb4fcf156f6c7de81365f86ae'

# ใช้งานฟังก์ชั่นเพื่อดึงข้อมูลจาก Longdo Map API
query = 'กรุงเทพมหานคร'
result = get_longdo_map(api_key, query)

# ตรวจสอบว่ามีข้อมูลหรือไม่และแสดงผล
if result:
    print('ข้อมูลที่พบ:')
    for location in result['data']:
        print(f'ชื่อ: {location["name"]}, ละติจูด: {location["lat"]}, ลองจิจูด: {location["lon"]}')

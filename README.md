# Hyperliquid Auto Trade by DK

แนะนำให้เริ่มต้นที่ $20 USD ขึ้นไป

หากไม่ได้ใช้เงินต้นเท่านี้ ต้องปรับการตั้งค่า size ให้เหมาะสมต่อการ Trade 1 ครั้งว่าให้เปิด size เท่าไหร่ ตามมูลค่าเงินทุนที่มี

-------------------
วิธีการติดตั้ง
-------------------

1. ติดตั้ง [Python](https://www.python.org/downloads/) และ [Git](https://git-scm.com/downloads)

2. สร้าง Account HyperLiquid ที่

Mainnet: https://app.hyperliquid.xyz/join/DEKKENG 

Testnet: https://app.hyperliquid-testnet.xyz/join/DEKKENG

3. โอนเงินเข้าไปในกระเป๋า และเปิด Enable Trading ให้เรียบร้อย 

4. สร้าง API key ใน 

Mainnet: https://app.hyperliquid.xyz/API 

Testnet: https://app.hyperliquid-testnet.xyz/API 

ก็อป Private Key เก็บไว้

5. เปิด Powershell 

6. พิมพ์คำสั่ง 

```
pip install -r .\requirements.txt
```

```
cp config.json.sample config.json
```

7. notepad config.json

แก้ไขการตั้งค่าต่างๆ 

แก้ไข ```is_testnet``` เป็น false หากต้องการใช้งานบน mainnet

แก้ไข ```secret_key``` เป็น Private Key ตอนที่สร้าง API Key ในข้อ 4

แก้ไข ```account_address``` เป็น Address กระเป๋าหลัก (ไม่ใช่กระเป๋า API นะครับ)

แก้ไข ```coin``` เหรียญที่ต้องการเปิด Order

แก้ไข ```size``` ขนาดต่อการเปิด Order 1 ครั้ง ตามหน่วยสกุล coin ที่ตั้งไว้ (แนะนำให้ตั้งค่าไว้น้อยกว่าจำนวน USD ที่มี ประมาณ 10% เพื่อป้องกันเงินไม่พอเปิด Order เมื่อราคาเปลี่ยนไป)

5. พิมพ์คำสั่ง 

```
python start.py
```
from app.database import SessionLocal
from app import models
import bcrypt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_default_data():
    pwhash = bcrypt.hashpw(bytes("123", 'utf-8'), bcrypt.gensalt())
    hpassword = pwhash.decode('utf8')
    db = SessionLocal()
    objects = [
	    models.User(username="Archie", fullname="Archibald Weng", password=hpassword),
	    models.User(username="Boris", fullname="Boris Tien", password=hpassword),
	    models.User(username="Larry", fullname="Larry Chuang", password=hpassword),
	    models.User(username="Thomas", fullname="Thomas Lin", password=hpassword),
	    models.User(username="Dora", fullname="Dora Yen", password=hpassword),
	    models.User(username="Wimy", fullname="Wimy Kuo", password=hpassword),
	    models.User(username="Kathy", fullname="Kathy Wu", password=hpassword),
	    
	    models.Task(taskname="TIIP", fullname="TIIP-全方位減碳系統服務平台開發計畫", organization="永智"),
	    models.Task(taskname="108高雄溫管", fullname="108年高雄市溫室氣體管理計畫", organization="臺中市政府環境保護局"),
	    models.Task(taskname="108台中溫減", fullname="108年台中市溫室氣體減量計畫", organization="臺中市政府環境保護局"),
	    models.Task(taskname="109台中溫減", fullname="109年台中市溫室氣體減量計畫", organization="臺中市政府環境保護局"),
	    models.Task(taskname="台電-風力", fullname="台灣電力公司風力發電計畫(一)抵換專案", organization="台灣電力股份有限公司環境保護處"),
	    models.Task(taskname="台電-太陽光電", fullname="台灣電力公司台中及興達太陽光電計畫", organization="台灣電力股份有限公司環境保護處"),
	    models.Task(taskname="108台電-碳限制計畫", fullname="台電公司碳限制管理及對策研析計畫", organization="台灣電力股份有限公司環境保護處"),
	    models.Task(taskname="尚承-盤查", fullname="尚承鋼鐵股份有限公司108年度溫室氣體盤查", organization="尚承鋼鐵股份有限公司"),
	    models.Task(taskname="尚承-抵換", fullname="尚承鋼鐵加熱爐能源效率提升及天然氣替代重油溫室氣體減量抵換專案", organization="尚承鋼鐵股份有限公司"),
	    models.Task(taskname="109低碳辦", fullname="109年臺中市低碳城市推動計畫", organization="臺中市政府環境保護局"),
	    models.Task(taskname="106CORSIA", fullname="推動我國國際航空業碳抵換及減量計畫第一期計畫", organization="交通部民用航空局"),
	    models.Task(taskname="109CORSIA", fullname="推動我國國際航空業碳抵換及減量計畫第二期計畫", organization="交通部民用航空局"),

	    models.Task(taskname="瑞振工業-盤查及SBTi專案", fullname="瑞振工業溫室氣體管理專案", organization="瑞振工業公司"),
	    models.Task(taskname="108台電-碳限制計畫", fullname="台電公司碳限制管理及對策研析計畫", organization="台灣電力股份有限公司環境保護處"),

	]
    db.bulk_save_objects(objects)
    db.commit()
    db.close()
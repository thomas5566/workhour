from app.database import SessionLocal
from . import models
import bcrypt


def create_default_data():
    pwhash = bcrypt.hashpw(bytes("123", 'utf-8'), bcrypt.gensalt())
    hpassword = pwhash.decode('utf8')
    db = SessionLocal()
    objects = [
        models.Department(department_name="營運策略部"),
        models.Department(department_name="氣候金融組"),
        models.Department(department_name="事業發展部(全球行銷組)"),
        models.Department(department_name="計畫別"),

        models.User(username="Archie", 
                    fullname="Archibald Weng",
                    password=hpassword, 
                    department_id=2
                    ),
        models.User(username="Boris", 
                    fullname="Boris Tien",
                    password=hpassword,
                    department_id=2,
                    checklistAll_permission=1),
        models.User(username="Larry", 
                    fullname="Larry Chuang",
                    password=hpassword,
                    department_id=2
                    ),
        models.User(username="Thomas",
                    fullname="Thomas Lin",
                    password=hpassword, 
                    is_superuser=True,
                    department_id=2 
                    ),
        models.User(username="Dora", 
                    fullname="Dora Yen",
                    password=hpassword,
                    department_id=3,
                    is_superuser=True,
                    checklistAll_permission=1
                    ),
        models.User(username="Wimy", 
                    fullname="Wimy Kuo",
                    password=hpassword,
                    department_id=3
                    ),
        models.User(username="Kathy", 
                    fullname="Kathy Wu",
                    password=hpassword,
                    department_id=3
                    ),


        models.Task(taskname="TIIP",
                    fullname="TIIP-全方位減碳系統服務平台開發計畫",
                    organization="永智"),
        models.Task(taskname="108高雄溫管",
                    fullname="108年高雄市溫室氣體管理計畫",
                    organization="高雄市政府環境保護局"),
        models.Task(taskname="108台中溫減",
                    fullname="108年台中市溫室氣體減量計畫",
                    organization="臺中市政府環境保護局"),
        models.Task(taskname="109台中溫減",
                    fullname="109年台中市溫室氣體減量計畫",
                    organization="臺中市政府環境保護局"),
        models.Task(taskname="台電-風力",
                    fullname="台灣電力公司風力發電計畫(一)抵換專案",
                    organization="台灣電力股份有限公司再生能源處"),
        models.Task(taskname="台電-太陽光電",
                    fullname="台灣電力公司台中及興達太陽光電計畫",
                    organization="台灣電力股份有限公司再生能源處"),
        models.Task(taskname="108台電-碳限制計畫",
                    fullname="台電公司碳限制管理及對策研析計畫",
                    organization="台灣電力股份有限公司環境保護處"),
        models.Task(taskname="尚承-盤查",
                    fullname="尚承鋼鐵股份有限公司108年度溫室氣體盤查",
                    organization="尚承鋼鐵股份有限公司"),
        models.Task(taskname="尚承-抵換",
                    fullname="尚承鋼鐵加熱爐能源效率提升及天然氣替代重油溫室氣體減量抵換專案",
                    organization="尚承鋼鐵股份有限公司"),
        models.Task(taskname="109低碳辦",
                    fullname="109年臺中市低碳城市推動計畫",
                    organization="臺中市政府環境保護局"),
        models.Task(taskname="106CORSIA",
                    fullname="推動我國國際航空業碳抵換及減量計畫第一期計畫",
                    organization="交通部民用航空局"),
        models.Task(taskname="109CORSIA",
                    fullname="推動我國國際航空業碳抵換及減量計畫第二期計畫",
                    organization="交通部民用航空局"),
        models.Task(taskname="107環保署",
                    fullname="溫室氣體碳市場機制國際合作計畫",
                    organization="行政院環境保護署"),
        models.Task(taskname="109港務公司",
                    fullname="臺灣港群溫室氣體自主盤查作業暨減量措施委託研究",
                    organization="台灣港務股份有限公司"),
        models.Task(taskname="台灣日東-碳權諮詢",
                    fullname="「無塵室換氣系統能源使用效率提升溫室氣體減量抵換專案」輔導確證及註冊計畫",
                    organization="台灣日東光學股份有限公司"),
        models.Task(taskname="東和鋼鐵-抵換",
                    fullname="「東和鋼鐵高雄廠型鋼加熱爐燃料修改抵換專案」監測及查證計畫",
                    organization="東和鋼鐵企業股份有限公司"),
        models.Task(taskname="裕融-盤查",
                    fullname="裕融企業股份有限公司「108年度溫室氣體盤查及查證作業」計畫",
                    organization="裕融企業股份有限公司"),
        models.Task(taskname="ECC碳權交易計畫",
                    fullname="SwiCity 生態圈 ECC碳權交易計畫",
                    organization="國立中興大學"),
        models.Task(taskname="109高雄溫管",
                    fullname="109-110年度高雄市溫室氣體管理計畫",
                    organization="高雄市政府環境保護局"),
        models.Task(taskname="GOGORO碳額度",
                    fullname="國際碳額度申請",
                    organization="GOGORO"),
        models.Task(taskname="109中技社綠運具",
                    fullname="綠運具政策之環境效益評估及整合",
                    organization="財團法人中技社"),
        models.Task(taskname="企業聯盟",
                    fullname="氣候行動企業聯盟計畫",
                    organization="國發會"),
        models.Task(taskname="台綜院溫管案",
                    fullname="台電公司因應溫室氣體減量及管理法研修之策略研析",
                    organization="台灣電力股份有限公司環境保護處(台綜院委託)"),
        models.Task(taskname="109環保署",
                    fullname="國際溫室氣體管理減量制度研析與交流合作計畫",
                    organization="行政院環境保護署"),
        models.Task(taskname="愛種樹-SROI報告書",
                    fullname="協助撰寫SROI報告書",
                    organization="愛種樹股份有限公司"),
        models.Task(taskname="亞泥-冷媒削減抵換",
                    fullname="申請抵換專案",
                    organization="亞洲水泥股份有限公司"),
        models.Task(taskname="台鎔科技-抵換",
                    fullname="申請抵換專案",
                    organization="台鎔科技材料股份有限公司"),
        models.Task(taskname="台灣志氯碳權",
                    fullname="申請抵換專案",
                    organization="台灣志氯股份有限公司"),
        models.Task(taskname="羽田生物-碳權",
                    fullname="申請抵換專案",
                    organization="羽田生物農業股份有限公司"),
        models.Task(taskname="尚承-ISO14001輔導計畫",
                    fullname="ISO14001輔導計畫",
                    organization="尚承鋼鐵股份有限公司"),
        models.Task(taskname="科建顧問合作案",
                    fullname="",
                    organization="科建顧問公司"),
        models.Task(taskname="瑞振工業-盤查及SBTi專案",
                    fullname="瑞振工業溫室氣體管理專案",
                    organization="瑞振工業公司"),
        models.Task(taskname="賴桑咖啡計畫",
                    fullname="申請抵換專案",
                    organization="賴桑咖啡"),
        models.Task(taskname="歐萊德碳權購買",
                    fullname="購買碳權",
                    organization="歐萊德國際股份有限公司"),
        models.Task(taskname="110台中溫減",
                    fullname="110年台中市溫室氣體盤查暨減量計畫",
                    organization="臺中市政府環境保護局"),
        models.Task(taskname="亞氨科技-碳權",
                    fullname="",
                    organization="亞氨科技股份有限公司"),
        models.Task(taskname="三芳化工-抵換",
                    fullname="",
                    organization="三芳化學工業股份有限公司"),
        models.Task(taskname="尚承-109年盤查及綠電諮詢",
                    fullname="",
                    organization="尚承鋼鐵股份有限公司"),
        models.Task(taskname="108台電-碳限制計畫",
                    fullname="台電公司碳限制管理及對策研析計畫",
                    organization="台灣電力股份有限公司環境保護處"),


        models.ExpenTask(expentask_name="廣告費"),
        models.ExpenTask(expentask_name="稅捐"),
        models.ExpenTask(expentask_name="文具印刷"),
        models.ExpenTask(expentask_name="郵電費"),
        models.ExpenTask(expentask_name="保險費"),
        models.ExpenTask(expentask_name="教育訓練費"),
        models.ExpenTask(expentask_name="雜費"),
        models.ExpenTask(expentask_name="委外費用"),
        models.ExpenTask(expentask_name="罰款"),
        models.ExpenTask(expentask_name="扣款"),

        # models.ExpenTask(expentask_name="旅費(出差費)"),
        # models.ExpenTask(expentask_name="折舊"),
        # models.ExpenTask(expentask_name="壞帳支出"),
        # models.ExpenTask(expentask_name="影印費"),
        # models.ExpenTask(expentask_name="修繕費"),
        # models.ExpenTask(expentask_name="自由捐贈"),
        # models.ExpenTask(expentask_name="各項攤提"),
        # models.ExpenTask(expentask_name="職工福利"),
        # models.ExpenTask(expentask_name="租金支出"),
    ]
    db.bulk_save_objects(objects)
    db.commit()
    db.close()

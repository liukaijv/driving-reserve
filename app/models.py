# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# # 科目枚举
EXAM_STAGE = ((1, u'科目一'), (2, u'科目二'), (3, u'科目三'), (4, u'科目四'), (5, u'已经毕业'))
EXAM_STAGE_STATUS = ((1, '不可约考'), (2, '约考成功'), (3, '考试通过'), (4, '考试未通过'))
IS_SUCCESS = ((False, u'<span class="text-danger">失败<span>'), (True, u'<span class="text-success">成功<span>'))
AUDIT_STATUS = (
    (-2, u'<span class="text-muted">已取消<span>'),
    (-1, u'<span class="text-danger">审核不通过<span>'),
    (0, u'<span class="text-info">待审核<span>'),
    (1, u'<span class="text-success">审核通过<span>')
)


class GetOrNoneManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class ClassCategory(models.Model):
    """ 学员所学的套餐 （教学班 1-5或者1-7） """
    name = models.CharField(max_length=50)
    fee = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)
    # 训练周期,列表存储
    training_weekdays = models.CharField(max_length=100)
    remarks = models.CharField(max_length=300, null=True, blank=True)

    objects = GetOrNoneManager()


    def __unicode__(self):
        return self.name


class TrainFrequency(models.Model):
    """    学员等级（训练频率，一周XX次，月周末XX次）    """
    name = models.CharField(max_length=50)
    # 每天的最多预约次数
    day_reserve_count = models.IntegerField(null=True, blank=True)
    # 每周的最多预约次数
    week_reserve_count = models.IntegerField(null=True, blank=True)
    # 每月的【周末】最多预约次数
    mouth_weekend_reserve_count = models.IntegerField(null=True, blank=True)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return self.name


class TrainingPlace(models.Model):
    """ 学车场地 """
    place_name = models.CharField(verbose_name=u'场地名称', max_length=100)
    guard_name = models.CharField(max_length=50, null=True, blank=True)
    guard_mobile = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.CharField(max_length=300, null=True, blank=True)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return self.place_name

    class Meta:
        ordering = ['-id', ]


class TrainTimeSpan(models.Model):
    """ 训练的时间段（教练车-上午，下午，晚上等）  """
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_stage = models.SmallIntegerField(max_length=1, choices=EXAM_STAGE, null=True)
    objects = GetOrNoneManager()

    def __unicode__(self):
        return self.name


class CoachCar(models.Model):
    """ 教练车信息  """
    TRAIN_TYPE = (
        ('C1', u'C1'),
        ('C2', u'C2'),
    )
    CAR_TYPE = (
        ('1', u'捷达'),
        ('2', u'桑塔纳'),
        ('3', u'新捷达'),
        ('4', u'新桑塔纳'),
        ('5', u'其他'),
    )

    license = models.CharField(max_length=10)
    train_type = models.CharField(max_length=2, choices=TRAIN_TYPE)
    car_type = models.CharField(max_length=1, choices=CAR_TYPE)
    training_place = models.ForeignKey(TrainingPlace, verbose_name=u'训练场地', on_delete=models.PROTECT)
    stage_two_train_time = models.CharField(max_length=100, null=True)
    stage_three_train_time = models.CharField(max_length=100, null=True)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return self.license


class DisabledDateTime(models.Model):
    """    禁用的日期时间    """
    coach_car = models.ForeignKey(CoachCar)
    begin_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return str(self.begin_datetime) + u" 至 " + str(self.end_datetime)


class CoachCarLog(models.Model):
    """    教练车日志记录    """
    coach_car = models.ForeignKey(CoachCar)
    behavior = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = GetOrNoneManager()


class UserManager(BaseUserManager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def create_user(self, mobile, id_card, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """

        now = timezone.now()
        if not mobile:
            raise ValueError('The given mobile must be set')
        user = self.model(mobile=mobile, id_card=id_card, password='',
                          is_active=True, is_superuser=False,
                          create_time=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, id_card, password):
        u = self.create_user(mobile, id_card, password)
        u.role_type = 0
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser):
    """ 学员信息 """
    TRAIN_TYPE = (
        ('C1', u'C1'),
        ('C2', u'C2'),
    )
    ROLE_TYPE = (
        (0, u'管理员'),
        (1, u'学员'),
        (2, u'教练')
    )
    IS_ACTIVE = (
        (False, u'否'),
        (True, u'是')
    )
    category = models.ForeignKey(ClassCategory, null=True, on_delete=models.PROTECT)
    coach_car = models.ForeignKey(CoachCar, null=True, on_delete=models.PROTECT)
    train_frequency = models.ForeignKey(TrainFrequency, null=True, on_delete=models.PROTECT)
    mobile = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    id_card = models.CharField(max_length=20, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=2, null=True)
    register_time = models.DateField(null=True, blank=True)
    exam_stage = models.SmallIntegerField(max_length=1, choices=EXAM_STAGE, null=True)
    exam_stage_status = models.SmallIntegerField(max_length=1, choices=EXAM_STAGE_STATUS, null=True)
    is_active = models.BooleanField(verbose_name=u'是否启用', choices=IS_ACTIVE, default=True)
    is_superuser = models.BooleanField(default=False)

    # 抵达次数
    arrival_count = models.IntegerField(default=0)
    # 爽约次数
    not_arrival_count = models.IntegerField(default=0)
    # 当前爽约次数，拉出黑名单使用
    current_not_arrival_count = models.IntegerField(default=0)
    # 是否进入黑名单
    is_blacklist = models.BooleanField(default=False)

    remarks = models.CharField(max_length=300, null=True, blank=True)
    role_type = models.SmallIntegerField(choices=ROLE_TYPE, default=1)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['id_card']

    def __unicode__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True

    @property
    def get_reserve_count(self):
        return DriveReserve.objects.filter(user=self.id, audit_status=1).count()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser


class UserLog(models.Model):
    """ 用户日志   """
    user = models.ForeignKey(User)
    is_background = models.BooleanField(default=False)
    behavior = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    objects = GetOrNoneManager()

    class Meta:
        ordering = ['-create_time']


class UserFeedback(models.Model):
    """    用户反馈    """
    AUDIT_STATUS = (
        (0, u'<span class="text-info">未处理<span>'),
        (1, u'<span class="text-success">已处理<span>')
    )
    user = models.ForeignKey(User)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    remarks = models.CharField(max_length=300, null=True, blank=True)
    audit_status = models.SmallIntegerField(max_length=1, choices=AUDIT_STATUS, default=0)
    audit_time = models.DateTimeField(null=True)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = GetOrNoneManager()


class DriveReserve(models.Model):
    """ 学员练车预约表  """
    SIGN_STATUS = (
        (-1, u'没到'),
        (0, u'待签'),
        (1, u'已签')
    )

    RESERVE_STYLE = (
        (True, u'后台'),
        (False, u'手机端')
    )
    user = models.ForeignKey(User)
    exam_stage = models.SmallIntegerField(max_length=1, choices=EXAM_STAGE)
    # 教练信息
    coach_id = models.IntegerField(null=True)
    coach_name = models.CharField(max_length=50, null=True)
    # 教练车信息
    coach_car_id = models.IntegerField(null=True)
    coach_car_license = models.CharField(max_length=10, null=True)
    # 训练场地信息
    training_place_id = models.IntegerField(null=True)
    training_place_name = models.CharField(max_length=100, null=True)
    # 预约时间信息
    train_time_span_id = models.IntegerField(null=True)
    train_time_span_name = models.CharField(max_length=100, null=True)
    train_time_span_start_time = models.TimeField(null=True)
    train_time_span_end_time = models.TimeField(null=True)

    train_date = models.DateField(null=True, blank=True)
    audit_status = models.SmallIntegerField(max_length=1, choices=AUDIT_STATUS, default=0)
    audit_time = models.DateTimeField(null=True)
    sign_status = models.SmallIntegerField(max_length=1, choices=SIGN_STATUS, default=0)
    is_alert = models.BooleanField(default=False)
    remarks = models.CharField(max_length=300, null=True, blank=True)
    is_admin_reserve = models.BooleanField(default=False, choices=RESERVE_STYLE)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    objects = GetOrNoneManager()

    @property
    def is_past_due(self):
        train_datetime = datetime.datetime.combine(self.train_date, self.train_time_span_end_time)
        if train_datetime > datetime.datetime.now():
            return False
        return True

    class Meta:
        ordering = ['-train_date', 'coach_car_id']


class ExamReserve(models.Model):
    """  考试预约表  """
    user = models.ForeignKey(User)
    exam_stage = models.SmallIntegerField(max_length=1, choices=EXAM_STAGE)
    create_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    audit_status = models.SmallIntegerField(max_length=1, choices=AUDIT_STATUS, default=0)
    audit_time = models.DateTimeField(null=True)
    remarks = models.CharField(max_length=300, null=True, blank=True)
    objects = GetOrNoneManager()


class SMSTemplate(models.Model):
    MESSAGE_TYPE = (
        (0, '短信'),
        (1, '站内消息')
    )
    """ 短信消息模板  """
    message_title = models.CharField(max_length=50, null=True, blank=True)
    message_content = models.CharField(max_length=200, null=True, blank=True)
    is_system = models.BooleanField(default=False)
    msg_type = models.SmallIntegerField(default=0, choices=MESSAGE_TYPE,
                                        null=True, blank=True)


class SMSSendLog(models.Model):
    """  短信发送日志  """
    user = models.ForeignKey(User)
    template = models.ForeignKey(SMSTemplate)
    send_content = models.CharField(max_length=200, null=True, blank=True)
    send_mobile = models.CharField(max_length=20, null=True, blank=True)
    send_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False, choices=IS_SUCCESS)
    objects = GetOrNoneManager()


class Config(models.Model):
    """ 系统配置    """
    reserve_overday = models.IntegerField(null=True, blank=True, default=7)
    is_open_blacklist = models.BooleanField(default=True)
    blacklist_break = models.IntegerField(null=True, blank=True, default=3)
    close_start_time = models.TimeField(null=True)
    close_end_time = models.TimeField(null=True)
    objects = GetOrNoneManager()
var monthNames = ["一月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月"
];
var dayNames = ["星期日， ", "星期一， ", "星期二， ", "星期三， ", "星期四， ", "星期五， ", "星期六， "]

var newDate = new Date();
newDate.setDate(newDate.getDate());
$('#Date').html(dayNames[newDate.getDay()] + newDate.getFullYear() + " " + monthNames[newDate.getMonth()] + newDate.getDate() + '号');

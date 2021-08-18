/*
  94 строка: внести id гугл таблицы в функцию.
  ID часть url адреса между  spreadsheets и edit - "spreadsheets/d/123456/edit" - в данном случае 123456
  Убедиться, что код запускается не с личного аккаунта пользователя,
  инчае это создаст все календари непосредственно в его гугл календаре.
*/
function CreateShedule(){
  
  var calendars = []
  /////////////////////////////
  var allCalendars = CalendarApp.getAllCalendars()
  var ExistCalendars = []
  for(i=0; i< allCalendars.length; i++)
  {
    ExistCalendars.push(allCalendars[i].getName())
  }
  var calendars = []
  var [names, emailList, Time, Events, EventColors] = GetSpreadsheetValues()
  let newNames = [];
  let newEmailList = [];
  names.forEach( value => {if(!ExistCalendars.includes(value[0])){
       newNames.push(value)
    }
  })
  emailList.forEach( value => {if(!emailList.includes(value[0])){
       newEmailList.push(value)
    }
  })
  Logger.log("New Names: " + newNames)
  /////////////////////////////////
  CreateShareCalendars(newNames, newEmailList)

  for (i=0; i<names.length; i++)
  {
    calendars.push(CalendarApp.getCalendarsByName(names[i]))
  }
  
  for (i=0; i<calendars.length; i++)
  {
    let startPeriod = GetDate(Time[0][0])
    let endPeriod = GetDate(Time[0][Time[0].length-1])
    let allEvents = calendars[i][0].getEvents(startPeriod, endPeriod)
    for (j=0; j<allEvents.length; j++)
    {
      // Clear calendar:
      allEvents[j].deleteEvent()
    }
    var NewEventsList = []
    var CalendarColorList = ["#039be5", "#33b679", "#7986cb", "#e67c73", "#f6bf26", "#f4511e", "#8e24aa", "#616161", "#3f51b5", "#0b8043","#d50000"]
    var prevEventName = null
    var prevEventColor = null
    for (j=0; j<Time[0].length-1; j++)
    {
      let startTime = GetDate(Time[0][j]);
      let endTime = GetDate(Time[0][j+1]);
      let eventName = Events[i][j];
      let eventColor = EventColors[i][j];
      if (prevEventName == null)
      {
        prevEventName = eventName;
        prevEventColor = eventColor;
        var prevStTime = startTime;
        var prevEndTime = endTime;
      }
      else if (prevEventColor == eventColor && (prevEventName == eventName || eventName == ""))
      {
        prevEndTime = endTime;
      }
      else
      {
        if (prevEventName != "")
        {
          let createdEvent = calendars[i][0].createEvent(prevEventName, prevStTime, prevEndTime);
          NewEventsList.push(createdEvent);
          let eventColor = FindNearestColor(prevEventColor, CalendarColorList)
          createdEvent.setColor(eventColor)
        }
        
        prevStTime = startTime;
        prevEndTime = endTime;
        prevEventName = eventName;
        prevEventColor = eventColor;
      }
      if (j == Time[0].length-2)
      {
        let createdEvent = calendars[i][0].createEvent(eventName, prevStTime, prevEndTime)
        NewEventsList.push(createdEvent);
        let eventColor = FindNearestColor(prevEventColor, CalendarColorList)
        createdEvent.setColor(eventColor)
      }
    }
  }
}


function GetSpreadsheetValues(){
  let spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[1]);
  let names = spreadsheet.getRange("A3:A4").getValues();
  let emailList = spreadsheet.getRange("B3:B4").getValues();
  let Time = spreadsheet.getRange("C1:M1").getDisplayValues();
  let Events = spreadsheet.getRange("C3:L4").getValues();
  let EventColors = spreadsheet.getRange("C3:L4").getBackgrounds();
  return [names, emailList, Time, Events, EventColors]
}
function CreateShareCalendars(newNames, newEmailList){
  let newCalendars = []
  for (i=0; i<newNames.length; i++)
  {
    CalendarApp.createCalendar(newNames[i])
    // newCalendars.push(CalendarApp.getCalendarsByName(newNames[i])[0].getId())
  }
  for (i=0; i< newNames.length; i++)
  {
    ShareCalendar(newEmailList[i][0], CalendarApp.getCalendarsByName(newNames[i])[0].getId())
  }
}

function GetDate(datetime){
  var reg = /(\d{2}).(\d{2}).(\d{4}) (\d{2}):(\d{2}):(\d{2})/;
  var dateArray = reg.exec(datetime); 
  var dateObject = new Date(
    (+dateArray[3]),
    (+dateArray[2])-1, // Careful, month starts at 0!
    (+dateArray[1]),
    (+dateArray[4]),
    (+dateArray[5]),
    (+dateArray[6])
  );
  return dateObject;
}

function FindNearestColor(color, colorList){
  let colorMinDist = 255*3;
  var colorToReturn = 0;
  for (t=0; t<colorList.length; t++){
    if (GetRGBdistance(color, colorList[t]) < colorMinDist)
    {
    colorMinDist = GetRGBdistance(color, colorList[t])
    colorToReturn = t
    }
  }
  return colorToReturn+1
}

function GetRGBdistance(color1, color2){
  let hex1 = hexToRgb(color1)
  let hex2 = hexToRgb(color2)
  return (hex1[0]-hex2[0])**2 + (hex1[1]-hex2[1])**2 + (hex1[2]-hex2[2])**2
}

function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if(result){
      var r= parseInt(result[1], 16);
      var g= parseInt(result[2], 16);
      var b= parseInt(result[3], 16);
      return [r, g, b]
  } 
  return null;
}

function ShareCalendar(userMail, calendarID)
{

  if (userMail != "")
  {
  var rule = {
    'scope': {
        'type': 'user',
        'value': userMail,
    },
    'role': 'writer'
  }
  created_rule = Calendar.Acl.insert(rule, calendarID)
  }
}

function onOpen()
{
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Синхронизация с календарем')
    .addItem('Создать расписание','CreateShedule')
    .addToUi();
}

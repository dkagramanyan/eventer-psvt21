// Run this function in App Script
function CreateShedule(){
  // Connect to Spreadsheet
  //var spreadsheet = SpreadsheetApp.getActiveSheet();// <- use if opened
  var spreadsheet = SpreadsheetApp.openById('PUT YOUR ID HERE');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[1]); // Select sheet
  var calendars = [] // There will be a calendar for aech person
  ///////////////////////////// Check for existing calendars with the same name
  var allCalendars = CalendarApp.getAllCalendars()
  var ExistCalendars = []
  for(i=0; i< allCalendars.length; i++)
  {
    ExistCalendars.push(allCalendars[i].getName())
  }
  var calendars = []

  let names = spreadsheet.getRange("A3:A4").getValues();
  let newNames = [];
  let emailList = spreadsheet.getRange("B3:B4").getValues();
  let newEmailList = [];
  names.forEach( value => {
    if(!ExistCalendars.includes(value[0])){
       newNames.push(value)
    }
  })
  emailList.forEach( value => {
    if(!emailList.includes(value[0])){
       newEmailList.push(value)
    }
  })
  Logger.log("New Names: " + newNames)
  /////////////////////////////////
  let newCalendars = []
  for (i=0; i<newNames.length; i++)
  {
    CalendarApp.createCalendar(newNames[i])
    newCalendars.push(CalendarApp.getCalendarsByName(newNames[i]))
  }
  for (i=0; i< newCalendars.length; i++)
  {
    ShareCalendar(newEmailList[i][0], newCalendars[i][0].getId())
  }
  // Make list of calendars
  for (i=0; i<Names.length; i++)
  {
    calendars.push(CalendarApp.getCalendarsByName(Names[i]))
  }
  ////////// TODO: Make a Fucntion, witch will get one range and parse it
  let Time = spreadsheet.getRange("C1:M1").getDisplayValues();
  let Events = spreadsheet.getRange("C3:L4").getValues();
  let EventColors = spreadsheet.getRange("C3:L4").getBackgrounds();
  
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
    // default calendar color list.
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

// Create Date object from strings
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

// Minimal color by RGBdistance metrics
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

// Count color metrics
function GetRGBdistance(color1, color2){
  let hex1 = hexToRgb(color1)
  let hex2 = hexToRgb(color2)
  return (hex1[0]-hex2[0])**2 + (hex1[1]-hex2[1])**2 + (hex1[2]-hex2[2])**2
}

// String with hexadecimal to Int
function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if(result){
      var r= Int(result[1], 16);
      var g= Int(result[2], 16);
      var b= Int(result[3], 16);
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

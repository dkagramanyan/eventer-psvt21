
function UpdateShedule()
{
  var calendars = []
  var [names, emailList, Time, Events, EventColors, DateZero] = GetSpreadsheetValues()
  for (i=0; i<names.length; i++)
  {
    calendars.push(CalendarApp.getCalendarsByName(names[i]))
  }
  var newTime = []
  let shift = 0
  for(j=0; j<Time[0].length; j++)
  {
    if (Time[0][j].length == 4.0)
      var reg = /(\d{1}):(\d{2})/;
    else
      var reg = /(\d{2}):(\d{2})/; 
    let currentTimeArray = reg.exec(Time[0][j]);
    if (j > 0)
    {
      var prevTime  = Time[0][j-1]
      if (prevTime.length == 4.0)
        var reg = /(\d{1}):(\d{2})/;
      else
        var reg = /(\d{2}):(\d{2})/;
      let prevTimeArray = reg.exec(prevTime);
      
      var tmp = (parseInt(currentTimeArray[1]) - parseInt(prevTimeArray[1])) * 60 + (parseInt(currentTimeArray[2]) - parseInt(prevTimeArray[2]))
      if (tmp < 0)
        shift += 1
    }
    let dateTime = GetTime(currentTimeArray, GetDate(DateZero), shift)
    newTime.push(dateTime)
  }
  for (i=0; i<calendars.length; i++)
  {
    let startPeriod = newTime[i]
    let endPeriod = newTime[newTime.length-1]
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
      let startTime = newTime[j];
      let endTime = newTime[j+1];
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
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[0]);
  let names = spreadsheet.getRange(ParseDiap()[0]).getValues();
  let emailList = spreadsheet.getRange(ParseDiap()[1]).getValues();
  let DateZero = spreadsheet.getRange("C1").getDisplayValues()[0][0];
  let Time = spreadsheet.getRange(ParseDiap()[2]).getDisplayValues();
  let Events = spreadsheet.getRange(ParseDiap()[3]).getValues();
  let EventColors = spreadsheet.getRange(ParseDiap()[3]).getBackgrounds();
  return [names, emailList, Time, Events, EventColors, DateZero]
}

function GetTime(timeArray, dateArray, shift){
  var dateObject = new Date(
    (+dateArray[3]),
    (+dateArray[2])-1, // Careful, month starts at 0!
    (+dateArray[1]),
    (+timeArray[1]),
    (+timeArray[2]),
  );
  dateObject.setDate(dateObject.getDate() + shift);
  return dateObject;
}

function GetDate(date){
  var reg = /(\d{2}).(\d{2}).(\d{4})/;
  var dateArray = reg.exec(date); 
  return dateArray;
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
  return Math.sqrt((hex1[0]-hex2[0])**2 + (hex1[1]-hex2[1])**2 + (hex1[2]-hex2[2])**2)
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
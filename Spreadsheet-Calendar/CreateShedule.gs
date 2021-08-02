// Run this function in App Script
function CreateShedule(){
  var spreadsheet = SpreadsheetApp.getActiveSheet();
  var spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[1]);
  var calendars = []
  /////////////////////////////
  var allCalendars = CalendarApp.getAllCalendars()
  var ExistCalendars = []
  for(i=0; i< allCalendars.length; i++)
  {
    ExistCalendars.push(allCalendars[i].getName())
  }
  var calendars = []

  var Names = spreadsheet.getRange("A3:A4").getValues();
  var NewNames = []
  Names.forEach( value => {
    if(!ExistCalendars.includes(value[0])){
      //  Logger.log(value + " at position " + Names.indexOf("value"))
       NewNames.push(value)
    }
  })
  Logger.log("New Names: " + NewNames)
  /////////////////////////////////
  for (i=0; i<NewNames.length; i++)
  {
    CalendarApp.createCalendar(NewNames[i])
  }
  for (i=0; i<Names.length; i++)
  {
    calendars.push(CalendarApp.getCalendarsByName(Names[i]))
  }
  let Time = spreadsheet.getRange("C1:K1").getDisplayValues();
  let Events = spreadsheet.getRange("C3:J4").getValues();
  let EventColors = spreadsheet.getRange("C3:J4").getBackgrounds();
  // Clear calendar:
  for (i=0; i<calendars.length; i++)
  {
    let startPeriod = GetDate(Time[0][0])
    let endPeriod = GetDate(Time[0][Time[0].length-1])
    let allEvents = calendars[i][0].getEvents(startPeriod, endPeriod)
    for (j=0; j<allEvents.length; j++)
    {
      allEvents[j].deleteEvent()
    }
    var NewEventsList = []
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
      else if (prevEventName == eventName || prevEventColor == eventColor)
      {
        prevEndTime = endTime;
      }
      else
      {
        if (prevEventName != "")
        {
          NewEventsList.push(calendars[i][0].createEvent(prevEventName, prevStTime, prevEndTime));
        }
        prevStTime = startTime;
        prevEndTime = endTime;
        prevEventName = eventName;
        prevEventColor = eventColor;
      }
      if (j == Time[0].length-2)
      {
        NewEventsList.push(calendars[i][0].createEvent(eventName, prevStTime, prevEndTime));
      }
    }
    // Some code for change events color
    /*
    for (j=0; j<NewEventsList.length; j++)
    {
      NewEventsList[j].setColor(EventColor[i][j])
    }
    */
  }
}

// Creates Date from String
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


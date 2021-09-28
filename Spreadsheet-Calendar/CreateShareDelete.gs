function CreateCalendars(){
  let spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[0]);
  let names = spreadsheet.getRange(ParseDiap()[0]).getValues();
  for (i=0; i < names.length; i++)
  {
    CalendarApp.createCalendar(names[i][0])
  }
  var range = SpreadsheetApp.getActive().getRange(ParseDiap()[4]);
  range.check();
}

function ShareCalendars(){
  let spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[0]);
  let names = spreadsheet.getRange(ParseDiap()[0]).getValues();
  let EmailList = spreadsheet.getRange(ParseDiap()[1]).getValues();
  for (i=0; i < names.length; i++)
  {
    if (EmailList[i][0] != "")
    {
      var rule = {'scope': {'type': 'user','value': EmailList[i][0],},'role': 'writer'}
      created_rule = Calendar.Acl.insert(rule, CalendarApp.getCalendarsByName(names[i][0])[0].getId())
    }
  }
}

function DeleteCalendars(){
  let spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[0]);
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Удалить календари', 'Введите диапазон в формате "A1:A3"', ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() !== ui.Button.CANCEL){
    var namesList = spreadsheet.getRange(ParseDiap()[0]);
    var namesToDelete = spreadsheet.getRange(response.getResponseText());
    if (areEqual(namesList, namesToDelete) == true){
      namesToDelete = namesToDelete.getValues()
      for (i=0; i < namesToDelete.length; i++)
      {
        CalendarApp.getCalendarsByName(namesToDelete[i][0])[0].deleteCalendar()
      }
      var range = SpreadsheetApp.getActive().getRange(ParseDiap()[4]);
      range.uncheck();
    }
    else
    {
      var response2 = ui.alert('Ошибка', 'Диапазон "' + response.getResponseText() + '" не в входит в диапазон', ui.ButtonSet.OK);
    }
    }
  else{
    var response2 = ui.alert('Ошибка', 'Диапазон "' + response.getResponseText() + '" не в формате "A1:A3"', ui.ButtonSet.OK);
  }
}

function areEqual(r1, r2) {
  return r1.getSheet().getName() == r2.getSheet().getName() 
         && r1.getRow() <= r2.getRow() 
         && r1.getColumn() == r2.getColumn()
         && r1.getWidth() == r2.getWidth()
         && r1.getHeight() >= r2.getHeight();
}



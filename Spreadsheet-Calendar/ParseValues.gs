function ParseDiap()
{
  // name, mail, time, events, checkboxes
  var arr = ['', 'A', 'B', 'C', 'D']
  var spreadsheet = SpreadsheetApp.openById('1xJJdpjHQddkx6Rnm6npW6O0VWKBNq4IkVsIP6Hszl_w');
  SpreadsheetApp.setActiveSheet(spreadsheet.getSheets()[0]);
  var diapStr = spreadsheet.getRange("B1").getValues();
  // var reg = /(\w{2}|\w{3}):(\w{2}|\w{3}),(\w{2}|\w{3}):(\w{2}|\w{3}),(\w{2}|\w{3}):(\w{3}|\w{2})/;
  var dataArray = diapStr[0][0].split(',')
  let names = spreadsheet.getRange(dataArray[0]);
  let timeLetters = dataArray[1].split(':')
  let rangeMail = arr[names.getColumn()+1] + dataArray[0][1] + ':' + arr[names.getColumn()+1] + dataArray[0][4]
  let rangeCheckbox = arr[names.getColumn()-1] + dataArray[0][1] + ':' + arr[names.getColumn()-1] + dataArray[0][4]
  let rangeEvents = timeLetters[0].slice(0, -1) + dataArray[0][1] + ':' + timeLetters[1].slice(0, -1) + dataArray[0][4]
  let toReturn = [dataArray[0], rangeMail, dataArray[1],rangeEvents, rangeCheckbox]
  return toReturn
}
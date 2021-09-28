function onOpen()
{
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Календарь')
    .addItem('Создать календари','CreateCalendars')
    .addItem('Удалить календари','DeleteCalendars')
    .addItem('Синхронизировать календарь','UpdateShedule')
    .addItem('Отправить приглашения','ShareCalendars')
    .addToUi();
}

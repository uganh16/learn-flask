$(function () {
  $('[data-toggle="tooltip"]').tooltip({
    title: () => {
      return moment($(this).data('timestamp')).format('lll');
    }
  });
});

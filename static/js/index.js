$(document).ready(function () {
  var formData = new FormData();
  $("#formFileMultiple").change(function () {
    var totalfiles = document.getElementById("formFileMultiple").files.length;
    for (var index = 0; index < totalfiles; index++) {
      formData.append(
        "files[]",
        document.getElementById("formFileMultiple").files[index]
      );
    }
  });

  $("form").submit((e) => {
    e.preventDefault();
    $(".spinner-border").show();
    $.ajax({
      url: "/uploader",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (data) {
        // console.log(data);
        $(".spinner-border").hide();
        $(".alert").show();
      },
      error: function (error) {
        $(".spinner-border").hide();
        alert("Something Went Wrong !");
      },
    });
  });
});

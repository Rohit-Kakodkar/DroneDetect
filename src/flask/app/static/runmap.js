$(document).ready(function () {

  console.log('init');

  $( "#all" ).click(function() {
    //alert( "Handler for .click() all." );
    // The location of Uluru
    var NY = {lat: 40.7128, lng: -74.0060};
    // The map, centered at Uluru
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 13, center: NY});
    // The marker, positioned at Uluru
    latitudes = {{latitudes}}
    longitudes = {{longitudes}}

    for (var j = 0; j<latitudes.length; j++){
      var marker = new google.maps.Marker({position: {lat: latitudes[j],
                                                      lng: longitudes[j]},
                                                      map: map});
    }
  });

  $( "#malfunctioning" ).click(function() {

    //alert( "Handler for .click() all." );
    // The location of Uluru
    var NY = {lat: 40.7128, lng: -74.0060};
    // The map, centered at Uluru
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 13, center: NY});
    // The marker, positioned at Uluru
    var marker = new google.maps.Marker({position: {lat: 40.7328,
                                                    lng: -74.0060},
                                         map: map});
    var marker = new google.maps.Marker({position: {lat: 40.7428,
                                                    lng: -74.0060},
                                         map: map});
  });

  $( "#crashed" ).click(function() {

    //alert( "Handler for .click() all." );
    // The location of Uluru
    var NY = {lat: 40.7128, lng: -74.0060};
    // The map, centered at Uluru
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 13, center: NY});
    // The marker, positioned at Uluru
    var marker = new google.maps.Marker({position: {lat: 40.7128,
                                                    lng: -74.0160},
                                         map: map});
    var marker = new google.maps.Marker({position: {lat: 40.7228,
                                                    lng: -74.0260},
                                         map: map});
  });
});

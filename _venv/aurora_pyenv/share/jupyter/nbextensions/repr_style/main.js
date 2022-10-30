/**
* ----------------------------------------------------------------------------
* ----------------------------------------------------------------------------
*/

define([
    "require",
    "jquery",
], function(
    requirejs,
    $
) {
    "use_strict";

    function add_css (url) {
		return $('<link/>').attr({
			type : 'text/css',
			rel : 'stylesheet',
			href : requirejs.toUrl(url)
		}).appendTo('head');
	}

    function add_script (url) {
		var s = document.createElement("script");
        s.type = "text/javascript";
        s.src = requirejs.toUrl(url);
        // Use any selector
        $("head").append(s);
	}
    var load_ipython_extension = function(background) {
        // Check if the extension is gettin loaded inside pro
        $.get(document.location.origin + "/custom/messages.js")
        .done(function() { 
            // do nothin as pro loads custom scripts proramatically
            // code path : /ArcGISDesktop/ArcGISGeoprocessing/ArcGIS.Desktop.GeoProcessing/ProNotebook/InterpreterStateManager.cs#L243
        }).fail(function() { 
            add_css("./custom.css");
            add_css("./messages.css");
            add_script("./messages.js");
            add_script("./custom.js");
        });
    };

    var extension = {
        load_ipython_extension : load_ipython_extension,
    };
    return extension;
});

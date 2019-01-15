odoo.define('website_iframe_snippet', function (require) {
'use strict';

var Model = require('web.Model');
var ajax = require('web.ajax');
var core = require('web.core');
var base = require('web_editor.base');
var web_editor = require('web_editor.editor');
var options = require('web_editor.snippets.options');
var snippet_editor = require('web_editor.snippet.editor');
var session = require('web.session');
var website = require('website.website');
var _t = core._t;
var Widget = require('web.Widget');
var contentMenu = require('website.contentMenu');

options.registry.website_iframe = options.Class.extend({
    drop_and_build_snippet: function() {
        var self = this;

	    website.prompt({
	        id: "editor_new_iframe",
			window_title: _t("Create Iframe"),
			input: "Enter URL",
		    init: function (field) {

                    var $group = this.$dialog.find("div.form-group");
                    $group.removeClass("mb0");

                    var $add = $(
                    '<div class="form-group">'+
                        '<label class="col-sm-3 control-label">Width</label>'+
                        '<div class="col-sm-9">'+
                        '  <input type="text" name="width" value="100%" class="form-control" required="required"/> '+
                        '</div>'+
                    '</div>'+
                    '<div class="form-group mb0">'+
                        '<label class="col-sm-3 control-label">Height</label>'+
                        '<div class="col-sm-9">'+
                        '  <input type="text" name="height" class="form-control" value="1000px"/>'+
                        '</div>'+
                    '</div>');
                    //$add.find('label').append(_t("Add page in menu"));
                    $group.after($add);

			        //return field;
			    },

        }).then(function (url, field_id, $dialog) {
            var width = $dialog.find('input[name="width"]').val();
            var height = $dialog.find('input[name="height"]').val();

			//Can't have an iframe inside snippet so recreate it here...
		    self.$target.html("<div class='container'><div class='row'><iframe src='" + url  + "' style='width:" + width + ";height:" + height + ";'/></div></div>");
        });
    },

});


});

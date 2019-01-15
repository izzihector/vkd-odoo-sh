odoo.define('web_iframe_widget.iframe', function (require) {
"use strict";

var core = require('web.core');
var Widget= require('web.Widget');
var field_registry = require('web.field_registry');
var widgetRegistry = require('web.widget_registry');
var FormView = require('web.FormView');
var FieldChar = field_registry.get('char');
var AbstractField = require('web.AbstractField');

console.log(field_registry,'field_registry')


var IframeWidget = FieldChar.extend({
    template: 'WebIframe',
    init: function () {
            this._super.apply(this, arguments);
    },
    _render: function() {
        console.log(this,'rrrr')
        var height = this.__node.attrs.height || 0.00
    	var width = this.__node.attrs.width || 0.00
        var url_value = this.value
        if (url_value=="") {
            this._super();
        } else {
            this.$el.find('iframe')
                    .attr('src', url_value)
                    .attr('height', height)
                    .attr('width', width);
        }
    },
})
field_registry.add(
    'iframe', IframeWidget
);

});
"use strict";

ckan.module('header-navtab-selector', function ($) {
    return {
      initialize: function () {
        var parentSelector = this.options.parent_selector;
        var cssClassToggle = this.options.css_class_toggle;

        this.el.children(parentSelector).each(function () {
          if ($(this).children('a').attr('href') !== "/" && window.location.pathname.includes($(this).children('a').attr('href'))) {
            $(this).children('div').addClass(cssClassToggle);
            $(this).children('a').css("font-weight", "bold");
          }
          if ($(this).children('a').attr('href') === "/" && window.location.pathname === ($(this).children('a').attr('href'))) {
            $(this).children('div').addClass(cssClassToggle);
            $(this).children('a').css("font-weight", "bold");
          }
        });
      }
    }
  }
);

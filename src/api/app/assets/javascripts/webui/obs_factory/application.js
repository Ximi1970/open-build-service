// This is a manifest file that'll be compiled into application.js, which will include all the files
// listed below.
//
// Any JavaScript/Coffee file within this directory, lib/assets/javascripts, vendor/assets/javascripts,
// or vendor/assets/javascripts of plugins, if any, can be referenced here using a relative path.
//
// It's not advisable to add code directly here, but if you do, it'll appear at the bottom of the
// the compiled file.
//
// WARNING: THE FIRST BLANK LINE MARKS THE END OF WHAT'S TO BE PROCESSED, ANY BLANK LINE SHOULD
// GO AFTER THE REQUIRES BELOW.
//
//= require jquery
//= require jquery.ui.menu
//= require jquery.ui.tooltip
//= require jquery_ujs
//= require cocoon
//= require moment
//= require mousetrap
//= require peek
//
//= require webui/obs_factory/keybindings.js
//= require webui/obs_factory/bento/script.js
//= require webui/obs_factory/bento/global-navigation.js
//= require webui/obs_factory/bento/l10n/global-navigation-data-en_US.js

function remove_dialog() {
    $(this).parents('.dialog:visible').remove();
    $('.overlay').hide();
}

function fillEmptyFields() {
    if (document.getElementById('username').value === '') {
        document.getElementById('username').value = "_";
    }
    if (document.getElementById('password').value === '') {
        document.getElementById('password').value = "_";
    }
}

function toggleBox(link, box) {
    //calculating offset for displaying popup message
    var leftVal = link.position().left + "px";
    var topVal = link.position().bottom + "px";
    $(box).css({
        left: leftVal,
        top: topVal
    }).toggle();
}

function callPiwik() {
    var u = (("https:" == document.location.protocol) ? "https://beans.opensuse.org/piwik/" : "http://beans.opensuse.org/piwik/");
    _paq.push(['setSiteId', 8]);
    _paq.push(['setTrackerUrl', u + 'piwik.php']);
    _paq.push(['trackPageView']);
    _paq.push(['setDomains', ["*.opensuse.org"]]);
    var d = document,
        g = d.createElement('script'),
        s = d.getElementsByTagName('script')[0];
    g.type = 'text/javascript';
    g.defer = true;
    g.async = true;
    g.src = u + 'piwik.js';
    s.parentNode.insertBefore(g, s);
}

$(document).ajaxSend(function (event, request, settings) {
    if (typeof(CSRF_PROTECT_AUTH_TOKEN) == "undefined") return;
    // settings.data is a serialized string like "foo=bar&baz=boink" (or null)
    settings.data = settings.data || "";
    settings.data += (settings.data ? "&" : "") + "authenticity_token=" + encodeURIComponent(CSRF_PROTECT_AUTH_TOKEN);
});

// Could be handy elsewhere ;-)
var URL_REGEX = /\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gi;

function change_role(obj) {
    var td = obj.parent("td");
    var type = td.data("type");
    var role = td.data("role");

    var url;
    var data = {project: $('#involved-users').data("project"), package: $('#involved-users').data("package"), role: role};
    data[type + 'id'] = td.data(type);
    if (obj.is(':checked')) {
        url = $('#involved-users').data("save-" + type);
    } else {
        url = $('#involved-users').data("remove");
    }

    $('#' + type + '_spinner').show();
    $('#' + type + '_table input').animate({opacity: 0.2}, 500);
    $('#' + type + '_table input').prop("disabled", true);

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        complete: function () {
            $('#' + type + '_spinner').hide();
            $('#' + type + '_table input').animate({opacity: 1}, 200);
            $('#' + type + '_table input').prop('disabled', false);
        }
    });
}

function collapse_expand(file_id) {
    var placeholder = $('#diff_view_' + file_id + '_placeholder');
    if (placeholder.attr('id')) {
        $.ajax({
            url: placeholder.parents('.table_wrapper').data("url"),
            type: 'POST',
            data: { text: placeholder.text(), uid: placeholder.data('uid') },
            success: function (data) {
                $('#diff_view_' + file_id).show();
                $('#diff_view_' + file_id + '_placeholder').html(data);
                $('#diff_view_' + file_id + '_placeholder').attr('id', '');
                use_codemirror(placeholder.data('uid'), true, placeholder.data("mode"));
                $('#collapse_' + file_id).show();
                $('#expand_' + file_id).hide();
            },
            error: function (data) {
                $('#diff_view_' + file_id).hide();
                $('#collapse_' + file_id).hide();
                $('#expand_' + file_id).show();
            },
        });
    } else {
        $('#diff_view_' + file_id).toggle();
        $('#collapse_' + file_id).toggle();
        $('#expand_' + file_id).toggle();
    }
}

$(function() {
  $('.show_dialog').on('click', function() {
    $($(this).data('target')).removeClass('hidden');
    $('.overlay').show();
  });
});

$(document).on('click','.close-dialog', function() {
  var target = $(this).data('target');
  if (target) {
    $(target).addClass('hidden');
    $('.overlay').hide();
  }
});

// show/hide functionality for text
$(function() {
  $('.show-hide').on('click', function() {
    var target = $(this).data('target');
    $(target).toggle();

    if ($(target).is(':hidden')) {
      $(this).text($(this).data('showtext'));
    }
    else {
      $(this).text($(this).data('hidetext'));
    }
  });
});

odoo.define('employee_breaktime.greeting_message', function (require) {
"use strict";

var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');

var _t = core._t;


var GreetingMessage = Widget.extend(BarcodeHandlerMixin, {
    template: 'EmpBreaktimeGreetingMessage',

    events: {
        "click .o_emp_breaktime_button_dismiss": function() { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
    },

    init: function(parent, action) {
        var self = this;
        this._super.apply(this, arguments);
        BarcodeHandlerMixin.init.apply(this, arguments);
        this.__on_barcode_scanned = function(barcode, target) {
            // alert('123');
            if ($.contains(target, self.el)) {
                self.on_barcode_scanned.call(self, barcode);
            }
        }

        // if no correct action given (due to an erroneous back or refresh from the browser), we set the dismiss button to return
        // to the (likely) appropriate menu, according to the user access rights
        if(!action.breaktime) {
            this.stop_listening();
            this.session.user_has_group('hr_attendance.group_hr_attendance_user').then(function(has_group) {
                if(has_group) {
                    self.next_action = 'employee_breaktime.emp_breaktime_action_kiosk_mode';
                } else {
                    self.next_action = 'employee_breaktime.emp_breaktime_action_my_breaktimes';
                }
            });
            return;
        }

        this.next_action = action.next_action || 'employee_breaktime.empl_breaktime_action_my_breaktimes';
        // no listening to barcode scans if we aren't coming from the kiosk mode (and thus not going back to it with next_action)
        if (this.next_action != 'employee_breaktime.emp_breaktime_action_kiosk_mode' && this.next_action.tag != 'emp_breaktime_kiosk_mode') {
            this.stop_listening();
        }
        this.breaktime = action.breaktime;
        // check in/out times displayed in the greeting message template.
        this.breaktime.check_in_time = (new Date((new Date(this.breaktime.check_in)).valueOf() - (new Date()).getTimezoneOffset()*60*1000)).toTimeString().slice(0,8);
        this.breaktime.check_out_time = this.breaktime.check_out && (new Date((new Date(this.breaktime.check_out)).valueOf() - (new Date()).getTimezoneOffset()*60*1000)).toTimeString().slice(0,8);
        this.previous_breaktime_change_date = action.previous_breaktime_change_date;
        this.employee_name = action.employee_name;
    },

    start: function() {
        if (this.breaktime) {
            this.breaktime.check_out ? this.farewell_message() : this.welcome_message();
        }
    },

    welcome_message: function() {
        var self = this;
        var now = new Date((new Date(this.breaktime.check_in)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
        this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 5000);

        if (now.getHours() < 5) {
            this.$('.o_emp_breaktime_message_message').append(_t("Good night"));
        } else if (now.getHours() < 12) {
            if (now.getHours() < 8 && Math.random() < 0.3) {
                if (Math.random() < 0.75) {
                    this.$('.o_emp_breaktime_message_message').append(_t("The early bird catches the worm"));
                } else {
                    this.$('.o_emp_breaktime_message_message').append(_t("First come, first served"));
                }
            } else {
                this.$('.o_emp_breaktime_message_message').append(_t("Good morning"));
            }
        } else if (now.getHours() < 17){
            this.$('.o_emp_breaktime_message_message').append(_t("Good afternoon"));
        } else if (now.getHours() < 23){
            this.$('.o_emp_breaktime_message_message').append(_t("Good evening"));
        } else {
            this.$('.o_emp_breaktime_message_message').append(_t("Good night"));
        }
        if(this.previous_breaktime_change_date){
            var last_check_out_date = new Date((new Date(this.previous_breaktime_change_date)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
            if(now.valueOf() - last_check_out_date.valueOf() > 1000*60*60*24*7){
                this.$('.o_emp_breaktime_random_message').html(_t("Glad to have you back, it's been a while!"));
            } else {
                if(Math.random() < 0.02){
                    this.$('.o_emp_breaktime_random_message').html(_t("If a job is worth doing, it is worth doing well!"));
                }
            }
        }
    },

    farewell_message: function() {
        var self = this;
        var now = new Date((new Date(this.breaktime.check_out)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
        this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 5000);

        if(this.previous_breaktime_change_date){
            var last_check_in_date = new Date((new Date(this.previous_breaktime_change_date)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
            if(now.valueOf() - last_check_in_date.valueOf() > 1000*60*60*12){
                this.$('.o_emp_breaktime_warning_message').append(_t("Warning! Last check in was over 12 hours ago.<br/>If this isn't right, please contact Human Resources."));
                clearTimeout(this.return_to_main_menu);
                this.stop_listening();
            } else if(now.valueOf() - last_check_in_date.valueOf() > 1000*60*60*8){
                this.$('.o_emp_breaktime_random_message').html(_t("Another good day's work! See you soon!"));
            }
        }

        if (now.getHours() < 12) {
            this.$('.o_emp_breaktime_message_message').append(_t("Have a good day!"));
        } else if (now.getHours() < 14) {
            this.$('.o_emp_breaktime_message_message').append(_t("Have a nice lunch!"));
            if (Math.random() < 0.05) {
                this.$('.o_emp_breaktime_random_message').html(_t("Eat breakfast as a king, lunch as a merchant and supper as a beggar"));
            } else if (Math.random() < 0.06) {
                this.$('.o_emp_breaktime_random_message').html(_t("An apple a day keeps the doctor away"));
            }
        } else if (now.getHours() < 17) {
            this.$('.o_em[_breaktime_message_message').append(_t("Have a good afternoon"));
        } else {
            if (now.getHours() < 18 && Math.random() < 0.2) {
                this.$('.o_emp_breaktime_message_message').append(_t("Early to bed and early to rise, makes a man healthy, wealthy and wise"));
            } else {
                this.$('.o_emp_breaktime_message_message').append(_t("Have a good evening"));
            }
        }
    },

    on_barcode_scanned: function(barcode) {
        var self = this;
        if (this.return_to_main_menu) {  // in case of multiple scans in the greeting message view, delete the timer, a new one will be created.
            clearTimeout(this.return_to_main_menu);
        }
        var hr_employee = new Model('hr.employee');
        hr_employee.call('breaktime_scan', [barcode, ])
            .then(function (result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
    },

    destroy: function () {
        clearTimeout(this.return_to_main_menu);
        this._super.apply(this, arguments);
    },
});

core.action_registry.add('emp_breaktime_greeting_message', GreetingMessage);

return GreetingMessage;

});
import * as Cookies from "js-cookie";
import $ from "jquery";

class User {
    constructor() {
        this.username = null;
        this.enrollmentStatusHash = null;
        this.populateFieldsFromCookie();

        if (!this.username) {
            // Ensure that enrollment data is removed if no user is logged in.
            window.localStorage.removeItem('enrollments');
            window.localStorage.removeItem('enrollmentStatusHash');
        }
    }

    populateFieldsFromCookie() {
        let cookieValue = Cookies.get(User.userInfoCookieName);

        if (cookieValue) {
            cookieValue = JSON.parse(cookieValue.replace(/\\054/g, ',').replace(/\\"/g, '"'));
            this.username = cookieValue.username;
            this.enrollmentStatusHash = cookieValue.enrollmentStatusHash;
        }
    }

    isEnrolledInCourseRun(courseRunId) {
        let localStorageHash = window.localStorage.getItem('enrollmentStatusHash');

        if (localStorageHash !== this.enrollmentStatusHash) {
            $.ajax({
                type: "GET",
                url: User.enrollmentApiUrl + '/enrollment',
                async: false
            }).done(function(data){
                debugger;
                console.log(data);
            });
        }
    }
}

User.userInfoCookieName = 'prod-edx-user-info';
User.enrollmentApiUrl = 'https://courses.edx.org/api/enrollment/v1';

export {User}

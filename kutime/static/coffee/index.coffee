jQuery ->

    $(document).ready ->
        v = localforage.getItem 'ip', (value) ->
            if value is null
                alert 'no value'
                v = '127.0.0.1'
                localForage.setItem 'ip', v
        alert v
        cols = $('#cols')
        depts = $('#depts')
        lectures = $('#lectures')
        timetable = $('#timetable')

        loadDept = (col_num) -> 
            depts.html ''
            ret = $.ajax
                type: 'get'
                url: 'dept/' + col_num + '/'
                success: (retData) ->
                    for dept, i in retData
                        option = $('<option></option>')
                        option.val dept.pk
                        option.text dept.fields.name

                        if i == 0
                            option.attr 'selected', 'selected'
                            loadLecture(dept.pk)

                        depts.append option


        loadLecture = (dept_num) ->
            lectures.html ''
            ret = $.ajax
                type: 'get'
                url: 'lec/' + dept_num + '/'
                success: (retData) ->
                    for lect in retData
                        lect = lect.fields
                        campus = if lect.campus == 'A' then '안암' else '세종'
                        
                        td = $('<td></td>')
                        lecture = $('<tr class="lecture"></tr>')

                        lecture.append td.clone().text campus
                        lecture.append td.clone().text lect.number
                        lecture.append td.clone().text lect.comp_div
                        lecture.append td.clone().text lect.title
                        lecture.append td.clone().text lect.professor
                        lecture.append td.clone().text lect.classroom
                        lecture.append td.clone().text lect.credit + ' (' + lect.time + ')'
                        lecture.append td.clone().text lect.dayAndPeriod
                        lecture.append td.clone().text lect.isRelative
                        lecture.append td.clone().text lect.isLimitStudent
                        lecture.append td.clone().text lect.isWaiting
                        lecture.append td.clone().text lect.isExchange
                        
                        lecture.data 'title', lect.title
                        lecture.data 'classroom', lect.classroom
                        lecture.data 'dp', lect.dayAndPeriod

                        lectures.append lecture

        lect_div_base_width = 
        lect_div_base_height = 
        
        added_lectures = []
        temp_lecture = {
            'title': ''
        }
            

        color_set = []
        drawLecture = (lecture, start_cell, length, isTemp) ->
            console.log start_cell
            lect_div_width = start_cell.css 'width'
            lect_div_height = (parseInt start_cell.css 'height') * length
            start_pos = start_cell.position()
            """
            if isTemp
                lect_div = temp_lecture
            else
                lect_div = $('<div></div>')
            """
            lect_div = $('<div class="lecture_timetable"></div>')
            lect_div.css 'background-color', 'grey'
            lect_div.css 'position', 'absolute'
            lect_div.css 'top', start_pos.top
            lect_div.css 'left', start_pos.left
            lect_div.width lect_div_width
            lect_div.height lect_div_height

            lect_div.text lecture.data 'title'
            """
            collision check need before draw
            """
            timetable.append lect_div


        Object.observe added_lectures, (changes) ->
            console.log added_lectures
            timetable.text ''
            for lec in added_lectures
                drawLecture lec['lecture'], lec['start_cell'], lec['length'], lec['isTemp']

        Object.observe temp_lecture, (changes) ->
            console.log 'temp'
        
        $(window).resize -> 
            timetable.text ''
            for lec in added_lectures
                drawLecture lec['lecture'], lec['start_cell'], lec['length'], lec['isTemp']
        
        days = ['월', '화', '수', '목', '금', '토']
        addLectureToTable = (lecture, isTemp) -> 
            lect_dp = lecture.data 'dp'
            lect_dp = lect_dp.split ','

            for dp in lect_dp
                dp = dp.split '('
                day = days.indexOf(dp[0])
                
                if (dp[1].search '-') is -1
                    period_start = dp[1][0]
                    period_end = period_start
                else
                    period = dp[1].split '-'
                    period_start = period[0]
                    period_end = period[1][0]
                 
                lect_info = [day, period_start, period_end]
                console.log lect_info
                """
                if isTemp
                    temp_lecture = lect_info
                else
                    added_lectures.push lect_info
                """
                start_cell = $('td[data-pos=' + day + '-' + period_start + ']')
                console.log start_cell 
                lect_length = if period_start == period_end then 1 else period_end - period_start + 1

                _lec = {
                    'lecture': lecture
                    'start_cell': start_cell
                    'length': lect_length
                    'isTemp': isTemp
                }

                added_lectures.push _lec


        loadDept(cols.val())

        cols.change ->
            loadDept $(this).val()

        depts.change ->
            loadLecture $(this).val()

        delay = 300
        clicks = 0
        timer = null

        clicked_lect = null
        lectures.on 'click', 'tr.lecture', (e) ->
            clicked_lect = $(this)
            clicks++

            if clicks == 1
                timer = setTimeout(->
                    addLectureToTable clicked_lect, false
                    clicks = 0
                , delay)
            else
                clearTimeout timer
                addLectureToTable clicked_lect, false
                clicks = 0

        lectures.on 'dbclic', 'tr.lecture', (e) ->
            e.preventDefault()

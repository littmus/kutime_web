jQuery ->

    $(document).ready ->
        v = localforage.getItem 'ip', (value) ->
            if value is null
                v = '127.0.0.1'
                localforage.setItem 'ip', v
        
        cols_major = $('#cols_major')
        depts_major = $('#depts_major')
        cols_etc = $('#cols_etc')
        depts_etc = $('#depts_etc')
        lectures = $('#lectures > tbody')
        lectures_selected = $('#lectures_selected > tbody')
        timetable = $('#timetable')

        lecture_template = $('<tr class="lecture"></tr>')
        td = $('<td></td>')
        getLectureRow = (lect) ->
            campus = if lect.campus == 'A' then '안암' else '세종'
                        
            lecture = lecture_template.clone()

            lecture.append td.clone().text campus
            lecture.append td.clone().text lect.number
            lecture.append td.clone().text lect.placement
            lecture.append td.clone().text lect.comp_div
            lecture.append td.clone().text lect.title
            lecture.append td.clone().text lect.professor
            lecture.append td.clone().text lect.credit + ' (' + lect.time + ')'
            if lect.classroom is null
                lecture.append td.clone()
            else
                lecture.append td.clone().text lect.classroom
            #lecture.append td.clone().text lect.dayAndPeriod
            lecture.append td.clone().text if lect.isRelative then '●' else  ''
            lecture.append td.clone().text if lect.isLimitStudent then '●' else ''
            lecture.append td.clone().text if lect.isWaiting then '●' else ''
            lecture.append td.clone().text if lect.isExchange then '●' else ''

            return lecture

        loadDept = (col_num, type) -> 
            depts = if type is 'M' then depts_major else depts_etc
            console.log depts
            depts.html ''
            ret = $.ajax
                type: 'get'
                url: 'dept/' + col_num + '/'
                success: (retData) ->
                    option_template = $('<option></option>')
                    for dept, i in retData
                        option = option_template.clone()
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

                        lecture = getLectureRow lect
                        lecture.data 'lecture', lect
                        lectures.append lecture

        lect_div_base_width = 
        lect_div_base_height = 
        
        added_lectures = []
            
        color_set = []
        used_color_set = []
        drawLecture = (lecture, start_cell, length, isTemp, index) ->
            console.log start_cell
            lect_div_width = start_cell.css 'width'
            lect_div_height = (parseInt start_cell.css 'height') * length
            start_pos = start_cell.position()

            lect_div = $('<div class="lecture_timetable"></div>')
            """
            if isTemp
                lect_div.css 'background-color', 'black'
            else
                lect_div.css 'background-color', 'grey'
            """
            lect_div.css 'position', 'absolute'
            lect_div.css 'top', start_pos.top
            lect_div.css 'left', start_pos.left - 15
            lect_div.width lect_div_width
            lect_div.height lect_div_height

            txt = lecture.title
            txt += '<br/>'
            txt += lecture.classroom
            lect_div.html txt

            lect_div.data 'index', index
            timetable.append lect_div


        Object.observe added_lectures, (changes) ->
            console.log added_lectures
            timetable.text ''
            lectures_selected.html ''

            for lec, index in added_lectures
                drawLecture lec['lecture'], lec['start_cell'], lec['length'], lec['isTemp'], index
                lectures_selected.append getLectureRow lec['lecture']

        
        $(window).resize -> 
            timetable.text ''
            for lec, index in added_lectures
                drawLecture lec['lecture'], lec['start_cell'], lec['length'], lec['isTemp'], index
        
        days = ['월', '화', '수', '목', '금', '토']
        addLectureToTable = (lecture) ->
            lect_dp = lecture.dayAndPeriod
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

                start_cell = $('td[data-pos=' + day + '-' + period_start + ']')
                console.log start_cell

                full = start_cell.data 'full'
                console.log full
                if full is undefined or full is false
                    start_cell.data 'full', true
                else
                    alert '해당 시간대에 강의가 이미 존재합니다!'
                    return

                lect_length = if period_start == period_end then 1 else period_end - period_start + 1

                _lec = {
                    'lecture': lecture
                    'start_cell': start_cell
                    'length': lect_length
                    'isTemp': false
                }

                added_lectures.push _lec


        loadDept cols_major.val(), 'M'
        loadDept cols_etc.val(), 'E'

        cols_major.change ->
            loadDept $(this).val(), 'M'

        depts_major.change ->
            loadLecture $(this).val()

        cols_etc.change ->
            loadDept $(this).val(), 'E'

        depts_etc.change ->
            loadLecture $(this).val()

        $('#lectures').bootstrapTable
            stripped: true
            height: 250


        $('#lectures_selected').bootstrapTable
            height: 250

        $('#lectures_selected').css 'margin-top', '-42px'

        #lectures_selected.html ''

        delay = 300
        clicks = 0
        timer = null
        clicked_lect = null
        lectures.on 'click', 'tr.lecture', (e) ->
            clicked_lect = $(this).data 'lecture'
            addLectureToTable clicked_lect, false

        hovered_lect = null
        lectures.on 'hover', 'tr.lecture', (e) ->
            #hovered_lect = $(this).data 'lecture'
            #drawLecture hovered_lect, 

        timetable.on 'click', 'div.lecture_timetable', (e) ->
            ret = confirm '강의를 삭제할까요?'
            if ret is true
                index = $(this).data 'index'
                lec = added_lectures[index]
                lec.start_cell.data 'full', false

                added_lectures.splice index, 1

        lectures_selected.on 'click', 'tr.lecture', (e) ->
            #
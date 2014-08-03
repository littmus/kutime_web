jQuery ->
    $.extend $.fn.bootstrapTable.defaults,
        formatNoMatches: ->
            '추가한 강의가 없습니다.'

    lecture_template = $('<tr class="lecture"></tr>')
    td = $('<td></td>')
    lect_template = $('<div class="lecture_timetable"></div>')
    span_template = $('<span></span>')
    option_template = $('<option></option>')

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
        
        getLectureRow = (lect) ->
            lecture = lecture_template.clone()

            campus = if lect.campus == 'A' then '안암' else '세종'
            lecture.append td.clone().text campus
            lecture.append td.clone().text lect.number
            lecture.append td.clone().text lect.placement
            lecture.append td.clone().text lect.comp_div
            lecture.append td.clone().text lect.title
            lecture.append td.clone().text lect.professor
            lecture.append td.clone().text lect.credit + ' (' + lect.time + ')'
            lecture.append td.clone().text lect.dayAndPeriod
            if lect.classroom is null
                lecture.append td.clone()
            else
                lecture.append td.clone().text lect.classroom
            lecture.append td.clone().text if lect.isEnglish then '●' else  ''
            lecture.append td.clone().text if lect.isRelative then '●' else  ''
            lecture.append td.clone().text if lect.isLimitStudent then '●' else ''
            lecture.append td.clone().text if lect.isWaiting then '●' else ''
            lecture.append td.clone().text if lect.isExchange then '●' else ''

            return lecture

        loadDept = (col_num, type) -> 
            depts = if type is 'M' then depts_major else depts_etc
            depts.html ''

            ret = $.ajax
                type: 'get'
                url: 'dept/' + col_num + '/'
                dataType: 'json'
                success: (retData) ->
                    
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
                dataType: 'json'
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
        drawLecture = (lecture, cell_length, isTemp, index) ->
            for cl in cell_length
                start_cell = cl.start_cell

                lect_div_width = start_cell.css 'width'
                lect_div_height = (parseInt start_cell.css 'height') * cl.length
                start_pos = start_cell.position()

                lect_div = lect_template.clone()
                if isTemp
                    lect_div.addClass 'temp_lecture'
                    lect_div.css 'background-color', 'grey'
                
                lect_div.css 'position', 'absolute'
                lect_div.css 'top', start_pos.top
                lect_div.css 'left', start_pos.left - 15
                lect_div.width lect_div_width
                lect_div.height lect_div_height

                span = span_template.clone()
                txt = lecture.title
                txt += '<br/>'
                txt += lecture.classroom
                span.html txt
                lect_div.html txt

                if index != null
                    lect_div.data 'index', index
                
                if cl.length == 1
                    #
                else
                    lect_div.css 'line-height', '50px'

                timetable.append lect_div


        Object.observe added_lectures, (changes) ->
            console.log added_lectures
            timetable.text ''
            lectures_selected.html ''
            current_credit = 0

            for lec, index in added_lectures
                lecture = lec['lecture']
                drawLecture lecture, lec['cell_length'], lec['isTemp'], index
                lectures_selected.append getLectureRow lecture
                current_credit += lecture.credit

            $('#current_credit').text '강의 ' + added_lectures.length + ' 개 / ' + current_credit + ' 학점'
        
        $(window).resize -> 
            timetable.text ''
            for lec, index in added_lectures
                drawLecture lec['lecture'], lec['cell_length'], lec['isTemp'], index
        
        days = ['월', '화', '수', '목', '금', '토']
        parseLecturePos = (lecture, isTemp) ->
            lect_dp = lecture.dayAndPeriod
            lect_dp = lect_dp.split ','

            cell_length = []

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

                if isTemp == false
                    full = start_cell.data 'full'
                    console.log full
                    if full is undefined or full is false
                        start_cell.data 'full', true
                    else
                        alert '해당 시간대에 강의가 이미 존재합니다!'
                        return

                lect_length = if period_start == period_end then 1 else period_end - period_start + 1
                cl = {
                    'start_cell': start_cell
                    'length': lect_length
                }
                cell_length.push cl

            return cell_length

        addLectureToTable = (lecture) ->
            cell_length = parseLecturePos lecture, false

            _lec = {
                'lecture': lecture
                'cell_length': cell_length
                'isTemp': false
            }

            added_lectures.push _lec


        loadDept cols_etc.val(), 'E'
        loadDept cols_major.val(), 'M'

        cols_major.change ->
            loadDept $(this).val(), 'M'

        depts_major.change ->
            loadLecture $(this).val()

        cols_etc.change ->
            loadDept $(this).val(), 'E'

        depts_etc.change ->
            loadLecture $(this).val()

        $('#tab_major').click ->
            loadLecture depts_major.val()

        $('#tab_etc').click ->
            loadLecture depts_etc.val()

        $('#lectures').bootstrapTable
            height: 250

        $('#lectures_selected').bootstrapTable
            height: 250

        $('#lectures_selected').css 'margin-top', '-42px'

        clicked_lect = null
        lectures.on 'click', 'tr.lecture', (e) ->
            clicked_lect = $(this).data 'lecture'
            addLectureToTable clicked_lect, false

        hovered_lect = null
        lectures.on 'mouseover', 'tr.lecture', (e) ->
            hovered_lect = $(this).data 'lecture'
            lec_pos = parseLecturePos hovered_lect, true
            drawLecture hovered_lect, lec_pos, true, null

        lectures.on 'mouseout', 'tr.lecture', (e) ->
            hovered_lect = null
            $('div.temp_lecture').each ->
                $(this).remove()

        # re-add dbclick for mobile support


        timetable.on 'click', 'div.lecture_timetable', (e) ->
            ret = confirm '강의를 삭제할까요?'
            if ret is true
                index = $(this).data 'index'
                lec = added_lectures[index]
                for cl in lec.cell_length
                    cl.start_cell.data 'full', false

                added_lectures.splice index, 1

        lectures_selected.on 'click', 'tr.lecture', (e) ->
            #
jQuery ->

    $(document).ready ->
        cols = $('#cols')
        depts = $('#depts')
        lectures = $('#lectures')

        loadDept = (col_num) -> 
            depts.html ''
            ret = $.ajax
                type: 'get'
                url: 'dept/' + col_num + '/'
                success: (retData) ->
                    for dept, i in retData
                        if i == 0
                            depts.append '<option value="' + dept.pk + '" selected>' + dept.fields.name + '</option>'
                            loadLecture(dept.pk)
                        else
                            depts.append '<option value="' + dept.pk + '">' + dept.fields.name + '</option>'

        loadLecture = (dept_num) ->
            lectures.html ''
            ret = $.ajax
                type: 'get'
                url: 'lec/' + dept_num + '/'
                success: (retData) ->
                    for lect in retData
                        lect = lect.fields
                        campus = if lect.campus == 'A' then '안암' else '세종'
                        lecture = $('<tr class="lecture">' +
                                    '<td>' + campus + '</td>' +
                                    '<td>' + lect.number + '</td>' +
                                    '<td>' + lect.placement + '</td>' +
                                    '<td>' + lect.comp_div + '</td>' +
                                    '<td>' + lect.title + '</td>' +
                                    '<td>' + lect.professor + '</td>' +
                                    '<td>' + lect.classroom + '</td>' +
                                    '<td>' + lect.credit + ' (' + lect.time + ')</td>' +
                                    '<td>' + lect.dayAndPeriod + '</td>' +
                                    '<td>' + lect.isRelative + '</td>' +
                                    '<td>' + lect.isLimitStudent + '</td>' +
                                    '<td>' + lect.isWaiting + '</td>' +
                                    '<td>' + lect.isExchange + '</td>' +
                                    '</tr>')
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
            

        Object.observe added_lectures, (changes) ->
            console.log 'added'

        Object.observe temp_lecture, (changes) ->
            console.log 'temp'

        color_set = []
        drawLecture = (lecture, start_pos, length, isTemp) ->
            lect_div_width = start_cell.css 'width'
            lect_div_height = (parseInt start_cell.css 'height') * length
        
            if isTemp
                lect_div = temp_lecture
            else
                lect_div = $('<div></div>')

            lect_div.css 'background-color', 'grey'
            lect_div.css 'position', 'absolute'
            lect_div.css 'top', start_pos.top
            lect_div.css 'left', start_pos.left
            lect_div.width lect_div_width
            lect_div.height lect_div_height

            lect_div.text lecture.data 'title'

            $('div#timetable').append lect_div

        drawAllLectures = ->
            
        
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
                if isTemp
                    temp_lecture = lect_info
                else
                    added_lectures.push lect_info
                
                start_cell = $('td[data-pos=' + day + '-' + period_start + ']')
                
                lect_length = if period_start == period_end then 1 else period_end - period_start + 1


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
                    addLectureToTable clicked_lect, true
                    clicks = 0
                , delay)
            else
                clearTimeout timer
                addLectureToTable clicked_lect, false
                clicks = 0

        lectures.on 'dbclic', 'tr.lecture', (e) ->
            e.preventDefault()

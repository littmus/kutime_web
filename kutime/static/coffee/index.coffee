# lo-dash custom template delimiters
_.templateSettings.interpolate = /{{([\s\S]+?)}}/g

jQuery ->
#   $.extend $.fn.bootstrapTable.defaults,
#        formatNoMatches: ->
#            '강의가 없습니다.'

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
        search_input = $('#search_input')
        
        getLectureRow = (lect) ->
            lecture = lecture_template.clone()
            lecture.attr 'id', lect.number + '-' + lect.placement

            lecture.append td.clone().text lect.number
            lecture.append td.clone().text lect.placement
            lecture.append td.clone().text lect.comp_div

            lecture.append td.clone().html lect.title
            lecture.append td.clone().text lect.professor
            lecture.append td.clone().text lect.credit + ' (' + lect.time + ')'
            lecture.append td.clone().text lect.dayAndPeriod
            if _.isNull lect.classroom
                lecture.append td.clone()
            else
                lecture.append td.clone().text lect.classroom
            lecture.append td.clone().text if lect.isEnglish then '●' else  ''
            lecture.append td.clone().text if lect.isRelative then '●' else  ''
            lecture.append td.clone().text if lect.isLimitStudent then '●' else ''
            lecture.append td.clone().text if lect.isWaiting then '●' else ''
            lecture.append td.clone().text if lect.isExchange then '●' else ''

            lecture.append td.clone().text lect.note
            
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
                        number = dept.fields.number
                        option.val number
                        option.text dept.fields.name

                        if i == 0
                            option.attr 'selected', 'selected'
                            
                            if type == 'M'
                                loadLecture number, ''
                            else if type == 'E'
                                if $('option:selected', cols_etc).closest('optgroup').index() == 0
                                    loadLecture number, 'A'
                                else
                                    loadLecture number, 'S'

                        depts.append option

        loadLecture = (dept_num, campus) ->
            lectures.html ''
            ret = $.ajax
                type: 'get'
                url: 'lec/' + campus + dept_num + '/'
                dataType: 'json'
                success: (retData) ->
                    for lect in retData
                        lect = lect.fields

                        lecture = getLectureRow lect
                        localforage.setItem lect.number + '-' + lect.placement, lect
                        lectures.append lecture
                                    
                    $('#lectures').bootstrapTable 'resetView'
                    $('#lectures_selected').bootstrapTable 'resetView'

        searchLecture = (q) ->
            lectures.html ''
            ret = $.ajax
                type: 'get'
                url: 'search/' + q + '/'
                dataType: 'json'
                success: (retData) ->
                    for lect in retData
                        lect = lect.fields

                        lecture = getLectureRow lect
                        localforage.setItem lect.number + '-' + lect.placement, lect
                        lectures.append lecture
                    
                    $('#lectures').bootstrapTable 'resetView'
                    $('#lectures_selected').bootstrapTable 'resetView'

        search_input.keyup (e) ->
            if e.keyCode == 13
                q = $(this).val()
                searchLecture q

        lect_div_base_width = 
        lect_div_base_height = 
        
        added_lectures = []
        color_set = ['#1abc9c', '#2ecc71', '#3498db', '#9b59b6', '#34495e']
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
                if not _.isNull lecture.classroom
                    txt += lecture.classroom
                span.html txt
                lect_div.html txt

                if not _.isNull index
                    lect_div.data 'index', index
                
                if cl.length == 1
                    #
                else
                    lect_div.css 'line-height', '50px'

                timetable.append lect_div


        Object.observe added_lectures, (changes) ->
            timetable.text ''
            lectures_selected.html ''
            current_credit = 0
            
            for lec, index in added_lectures
                lecture = lec['lecture']
                drawLecture lecture, lec['cell_length'], lec['isTemp'], index
                lectures_selected.append getLectureRow lecture
                current_credit += lecture.credit
            
            t = _.template '강의 {{ l }} 개 / {{ c }} 학점', {
                'l': added_lectures.length
                'c': current_credit
            }

            $('#current_credit').text t
            $('#lectures_selected').bootstrapTable 'resetView'
        
        $(window).resize ->
            timetable.text ''
            for lec, index in added_lectures
                drawLecture lec['lecture'], lec['cell_length'], lec['isTemp'], index
            
            $('#lectures').bootstrapTable 'resetView'
            $('#lectures_selected').bootstrapTable 'resetView'

        days = ['월', '화', '수', '목', '금', '토']
        parseLecturePos = (lecture, isTemp) ->
            lect_dp = lecture.dayAndPeriod
            lect_dp = lect_dp.split ','

            cell_length = []

            for dp in lect_dp
                dp = dp.split '('
                day = days.indexOf(dp[0])
                
                if (dp[1].search '-') is -1
                    period_start = parseInt dp[1]
                    period_end = period_start
                else
                    period = dp[1].split '-'
                    period_start = period[0]
                    period_end = parseInt period[1]
                 
                lect_info = [day, period_start, period_end]

                start_cell = $('td[data-pos=' + day + '-' + period_start + ']')
                
                if isTemp == false
                    full = start_cell.data 'full'
                    if full is undefined or full is false
                        start_cell.data 'full', true
                    else
                        alert '해당 시간대에 강의가 이미 존재합니다!'
                        return

                    if period_start != period_end
                        end_cell = $('td[data-pos=' + day + '-' + period_end + ']')

                        efull = end_cell.data 'full'
                        if efull is undefined or efull is false
                            end_cell.data 'full', true
                        else
                            alert '해당 시간대에 강의가 이미 존재합니다!'
                            return

                lect_length = period_end - period_start + 1
                cl = {
                    'start_cell': start_cell
                    'length': lect_length
                }
                cell_length.push cl

            return cell_length

        addLectureToTable = (lecture) ->
            cell_length = parseLecturePos lecture, false
            if cell_length is undefined
                return

            _lec = {
                'lecture': lecture
                'cell_length': cell_length
                'isTemp': false
            }

            added_lectures.push _lec

        $('#lectures').bootstrapTable
            height: 250

        $('#lectures_selected').bootstrapTable
            height: 250

        #loadDept cols_etc.val(), 'E'
        loadDept cols_major.val(), 'M'

        cols_major.change ->
            loadDept $(this).val(), 'M'

        depts_major.change ->
            loadLecture $(this).val(), ''

        cols_etc.change ->
            loadDept $(this).val(), 'E'

        depts_etc.change ->
            if $('option:selected', cols_etc).closest('optgroup').index() == 0
                loadLecture $(this).val(), 'A'
            else
                loadLecture $(this).val(), 'S'

        $('#tab_major').click ->
            loadLecture depts_major.val(), ''

        $('#tab_etc').click ->
            if depts_etc.children().length == 0
                loadDept cols_etc.val(), 'E'
            else
                loadLecture depts_etc.val(), 'A'

        lectures.on 'click', 'tr.lecture a', (e) ->
            e.stopPropagation()

        lectures.on 'click', 'tr.lecture', (e) ->
            localforage.getItem $(this).attr('id'), (err, lect) ->
                addLectureToTable lect, false

        lectures.on 'mouseover', 'tr.lecture', (e) ->
            localforage.getItem $(this).attr('id'), (err, lect) ->
                lec_pos = parseLecturePos lect, true
                drawLecture lect, lec_pos, true, null

        lectures.on 'mouseout', 'tr.lecture', (e) ->
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

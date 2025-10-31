/*
 adapted from code at https://weblogs.asp.net/dwahlin/creating-a-line-chart-using-the-html-5-canvas
 */
var CanvasChart = function () {
    var ctx;
    var margin = { top: 60, left: 120, right: 0, bottom: 75 };
    var chartHeight, chartWidth, yMax, xMax, data;
    var maxYValue = 0;
    var minYValue = 0;
    var ratio = 0;
    var renderType = { lines: 'lines', points: 'points' };

    var render = function(canvasId, dataObj) {
        data = dataObj;
        getMaxDataYValue();
        var canvas = document.getElementById(canvasId);
        chartHeight = canvas.getAttribute('height');
        chartWidth = canvas.getAttribute('width');
        xMax = chartWidth - (margin.left + margin.right);
        yMax = chartHeight - (margin.top + margin.bottom);
        minYValue = Math.min(...dataObj.dataPoints.map(p => p.y));
        maxYValue = Math.max(...dataObj.dataPoints.map(p => p.y));
        ratio = yMax / ((maxYValue - minYValue) * 1.2);
        ctx = canvas.getContext("2d");
        renderChart();
    };

    var renderChart = function () {
        renderText();
        renderLinesAndLabels();

        if (data.renderTypes == undefined || data.renderTypes == null) data.renderTypes = [renderType.lines];
        for (var i = 0; i < data.renderTypes.length; i++) {
            renderData(data.renderTypes[i]);
        }
    };

    var getMaxDataYValue = function () {
        for (var i = 0; i < data.dataPoints.length; i++) {
            if (data.dataPoints[i].y > maxYValue) maxYValue = data.dataPoints[i].y;
        }
    };

    var renderText = function() {
        var labelFont = (data.labelFont != null) ? data.labelFont : '20pt Arial';
        ctx.font = labelFont;
        ctx.textAlign = "center";

        var txtSize = ctx.measureText(data.title);
        ctx.fillText(data.title, (chartWidth / 2), (margin.top / 2));
        
        txtSize = ctx.measureText(data.xLabel);
        ctx.fillText(data.xLabel, margin.left + (xMax / 2), yMax + margin.top + (margin.bottom / 1.5));

        ctx.save();
        ctx.rotate(-Math.PI / 2);
        ctx.font = labelFont;
        ctx.fillText(data.yLabel, ((yMax + margin.top) / 2) * -1, 20);
        ctx.restore();
    };

    var renderLinesAndLabels = function () {
        var yInc = yMax / 10;
        var yPos = 0;
        var yLabelInc = (maxYValue - minYValue) / 10;
        var xInc = getXInc();
        var xPos = margin.left;
        
        // Draw Y-axis gridlines and labels
        ctx.font = (data.dataPointFont != null) ? data.dataPointFont : '10pt Calibri';
        ctx.textAlign = "right";
        
        for (var i = 0; i <= 10; i++) {
            yPos = margin.top + (i * yInc);
            
            drawLine(margin.left, yPos, xMax + margin.left, yPos, '#E8E8E8');
            
            var labelValue = maxYValue - (i * yLabelInc);
            var txt = Math.round(labelValue) + " BPM";
            ctx.fillText(txt, margin.left - 10, yPos + 4);
        }
        
        // Draw X-axis labels
        ctx.textAlign = "center";
        for (var i = 0; i < data.dataPoints.length; i += Math.ceil(data.dataPoints.length / 10)) {
            txt = data.dataPoints[i].x;
            ctx.fillText(txt, xPos, yMax + margin.top + (margin.bottom / 3));
            xPos += xInc * Math.ceil(data.dataPoints.length / 10);
        }

        drawLine(margin.left, margin.top, margin.left, yMax + margin.top, 'black');

        drawLine(margin.left, yMax + margin.top, xMax + margin.left, yMax + margin.top, 'black');
    };

    var renderData = function(type) {
        var xInc = getXInc();
        var prevX = 0, prevY = 0;
        for (var i = 0; i < data.dataPoints.length; i++) {
            var pt = data.dataPoints[i];
            var ptY = (maxYValue - pt.y) * ratio + margin.top;
            if (ptY < margin.top) ptY = margin.top;
            var ptX = (i * xInc) + margin.left;
            if (i > 0 && type == renderType.lines) {
                drawLine(prevX, prevY, ptX, ptY, 'black', 2);
            }
            if (type == renderType.points) {
                ctx.beginPath();
                ctx.arc(ptX, ptY, 4, 0, 2 * Math.PI, false);
                ctx.fillStyle = '#000';
                ctx.fill();
                ctx.closePath();
            }
            prevX = ptX;
            prevY = ptY;
        }
    };

    var getXInc = function() {
        return xMax / (data.dataPoints.length - 1);
    };

    var drawLine = function(startX, startY, endX, endY, strokeStyle, lineWidth) {
        if (strokeStyle != null) ctx.strokeStyle = strokeStyle;
        if (lineWidth != null) ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        ctx.closePath();
    };

    return {
        renderType: renderType,
        render: render
    };
} ();
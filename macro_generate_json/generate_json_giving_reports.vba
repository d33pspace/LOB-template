Public json_sheet As Worksheet
Sub Generate_Json()

Dim process_file As Workbook
Dim this_file As Workbook
Set this_file = ActiveWorkbook
UserForm1.Show
If Stopped Then Exit Sub
If file = "" Then
    MsgBox "No File selected"
    End
End If

Set process_file = Workbooks(file)
process_file.Activate
process_file.Sheets.Add(After:=process_file.Sheets(process_file.Sheets.Count)).Name = "Json_Output"
Set json_sheet = Worksheets("Json_Output")

process_file.Sheets(1).Activate
ActiveSheet.Copy After:=process_file.Sheets(process_file.Worksheets.Count)
ActiveSheet.Name = "JSON_Working"
Range("C:C,E:E,G:G,J:J,M:M").EntireColumn.Delete
Range("A1").Select
Range("A:A").Insert Shift:=xlToRight

Range("C1").Select

Do While VBA.UCase(ActiveCell.Value) <> VBA.UCase("Invoice Date")
    ActiveCell.EntireRow.Delete
    Range("C1").Select
Loop

Range("A1").Value = "Contact Name"

end_row = Range("B1048576").End(xlUp).Row + 1
Dim i As Long
Dim k As Long
For i = 2 To end_row
    If Range("C" & i).Value = "" And VBA.InStr(1, Range("B" & i).Value, "Total") = 0 Then
        If Range("B" & i).Value <> "" Then
            k = 0
            Do While UCase(Range("B" & i).Offset(k, 0).Value) <> VBA.UCase("Total " & Range("B" & i).Value)
                    k = k + 1
            Loop

          Call JSON_VAL(i, i + k)
          i = i + k
        End If
    End If
Next i

Application.DisplayAlerts = False
process_file.Sheets("JSON_Working").Delete
Application.DisplayAlerts = True
this_file.Activate
MsgBox "completed"

End Sub

Sub JSON_VAL(start_row As Long, end_row As Long)


Dim DQ As String
DQ = VBA.Chr(34)
Dim JSON_start As String
JSON_start = "{" & DQ & "contactName" & DQ & ": " & DQ & Range("B" & start_row).Value & DQ & "," & DQ & "lineItems" & DQ & ": ["
JSON_split = ""
JSON_ALL = JSON_start
For i = start_row + 1 To end_row - 1
    JSON_LINE = ""
    If i >= start_row + 2 Then JSON_split = "," Else JSON_split = ""
    JSON_C1 = "{" & DQ & "invoiceNumber" & DQ & ": " & DQ & Range("B" & i).Value & DQ & ","
    JSON_C2 = DQ & "invoiceDate" & DQ & ": " & DQ & Range("C" & i).Value & DQ & ","
    JSON_C3 = DQ & "reference" & DQ & ": " & DQ & Range("D" & i).Value & DQ & ","
    JSON_C4 = DQ & "description" & DQ & ": " & DQ & VBA.Trim(Application.WorksheetFunction.Clean(VBA.Replace(Range("E" & i).Value, DQ, "\" & DQ))) & DQ & ","
    JSON_C5 = DQ & "unitPriceSource" & DQ & ": " & DQ & Range("F" & i).Value & DQ & ","
    
    Dim currencyRateVal As String
    If IsNumeric(Range("G" & i).Value) And Range("G" & i).Value <> 0 Then
        currencyRateVal = Format(CDbl(Range("F" & i).Value) / CDbl(Range("G" & i).Value), "0.00")
    Else
        currencyRateVal = "0.00"
    End If
    JSON_C6 = DQ & "currencyRate" & DQ & ": " & DQ & currencyRateVal & DQ & ","
    
    JSON_C7 = DQ & "invoiceTotalUSD" & DQ & ": " & DQ & Range("G" & i).Value & DQ & ","
    JSON_C8 = DQ & "originalCurrency" & DQ & ": " & DQ & Range("H" & i).Value & DQ & ","
    JSON_C9 = DQ & "method" & DQ & ": " & DQ & Range("I" & i).Value & DQ & "}"
    JSON_LINE = JSON_split & JSON_C1 & JSON_C2 & JSON_C3 & JSON_C4 & JSON_C5 & JSON_C6 & JSON_C7 & JSON_C8 & JSON_C9
    JSON_ALL = JSON_ALL & JSON_LINE
Next i
'op_end_row = Range("B1048576").End(xlUp).Row
'If end_row = op_end_row - 1 Then
    JSON_ALL = JSON_ALL & "] }"
'Else
'    JSON_ALL = JSON_ALL & "] } , "
'End If

data_row = json_sheet.Range("A1048576").End(xlUp).Row + 1
json_sheet.Range("A" & data_row).Value = Range("B" & start_row).Value
If VBA.Len(JSON_ALL) >= 32767 Then
    json_sheet.Range("B" & data_row).Value = "OVERFLOW"
Else
    json_sheet.Range("B" & data_row).Value = JSON_ALL
End If

End Sub

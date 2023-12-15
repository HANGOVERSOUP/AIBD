import * as React from 'react';
import { useEffect , useState} from 'react';
import axios from 'axios';


import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/DeleteOutlined';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Close';
import {
  GridRowModes,
  DataGrid,
  GridToolbarContainer,
  GridActionsCellItem,
  GridRowEditStopReasons,
} from '@mui/x-data-grid';

// 
// net수정페이지 -> 왼쪽 전체테이블 컴포넌트
// 
// 

export default function FullFeaturedCrudGrid({file,fileque,onDataReceived }) {
  // console.log("editnet_wholefile",file);
  // console.log("editnet_wholefileq",fileque);
  const [rows, setRows] = useState([]);
  const [rowModesModel, setRowModesModel] = React.useState({});

  const [uploadrows,setuploadrows] = useState([]);
  const [apicolumns,setapicolumns]=useState();

  const[net,setnet] = useState([]);

  const [updatedDataReceived, setUpdatedDataReceived] = useState('notupdated');
  const [forceRender, setForceRender] = useState(false);

  function EditToolbar(props) {
    const { setRows, setRowModesModel } = props;
  
    const handleClick = () => {
      const id = rows[rows.length-1].id +1 ;

      setRows((oldRows) => [...oldRows, { id,  isNew: true }]);
      setRowModesModel((oldModel) => ({
        ...oldModel,
        [id]: { mode: GridRowModes.Edit, fieldToFocus: 'name' },
      }));
    };
  
    return (
      <GridToolbarContainer>
        <Button color="primary" startIcon={<AddIcon />} onClick={handleClick}>
          Add record
        </Button>
      </GridToolbarContainer>
    );
  }


  // 데이터 전체
  const fetchData = async () => {
    try {
      const params = {
        question: fileque
      };
      const queryString = new URLSearchParams(params).toString();
      const myurl = `http://115.68.193.117:9999/net/data-check?p_name=${file}&${queryString}`;
      // console.log("edit_whole_myurl,",myurl);
      // console.log("edit_whole_queryString,",queryString);

      const response = await axios.get(myurl);
      const responseData = response.data;

      if (typeof responseData === 'string') {
        const parsedData = JSON.parse(responseData);

        if (typeof parsedData === 'object' && !Array.isArray(parsedData)) {
          const dataArray = Object.keys(parsedData).map(key => parsedData[key]);

          const columns = dataArray.length > 0 ? Object.keys(dataArray[0]) : [];
          setapicolumns(columns);

          setRows(dataArray);
        } else {
          console.error('Received data is not an object:', parsedData);
        }
      } else {
        console.error('Received data is not a string:', responseData);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  // 왼쪽 NET 드롭다운 리스트 api 호출
  const fetchData_net = async () => {
    try {
      // const myurl = `http://115.68.193.117:8000/net/file-json-tt?filename=${file}`;
      // const myurl = `http://115.68.193.117:8000/net/net-t?filename=LG_gram_data`;
      const myurl = `http://115.68.193.117:9999/net/net_info?p_name=${file}`;
      
      // console.log("myurl,",myurl);
      const response = await axios.get(myurl);
      const responseData = response.data;
      const netArray = [];
      // console.log("fetchData_net_responseData",responseData);

      // const netData = JSON.parse(responseData);
      const netData = responseData;

      for(const key in netData) {
        const netValue = netData[key].net_text;
        netArray.push(netValue);
      }
      // console.log("netArray",netArray);
      setnet(netArray);

    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  // fetchData 데이터 전체 , fetchData_net NET 목록
  // file 변동으로 useEffect 이나 실험 필요
  useEffect(() => {
    fetchData();
    fetchData_net();
  }, [file,fileque]);

  useEffect(() => {
    if(onDataReceived==='updated'){
      fetchData(file);
      fetchData_net(file);
      // console.log("onDataReceived_before",onDataReceived);
      setUpdatedDataReceived('complete'); 
      // console.log("onDataReceived_after",onDataReceived);
      setForceRender(prev => !prev);
    }else{
      // console.log("onDataReceived_else",onDataReceived);
    }
  }, [onDataReceived]);


  const handleRowEditStop = (params, event) => {
    if (params.reason === GridRowEditStopReasons.rowFocusOut) {
      event.defaultMuiPrevented = true;
    }
  };

  const handleEditClick = (id) => () => {
    setRowModesModel({ ...rowModesModel, [id]: { mode: GridRowModes.Edit } });
  };

  const handleSaveClick = (id) => () => {
    setRowModesModel({ ...rowModesModel, [id]: { mode: GridRowModes.View } });
    
  };

  // 삭제
  const handleDeleteClick = (id) => () => {
    setRows(rows.filter((row) => row.id !== id));
    // console.log("deleteaa",rows.filter((row) => row.id !== id))

  };

  const handleCancelClick = (id) => () => {
    setRowModesModel({
      ...rowModesModel,
      [id]: { mode: GridRowModes.View, ignoreModifications: true },
    });

    const editedRow = rows.find((row) => row.id === id);
    if (editedRow.isNew) {
      setRows(rows.filter((row) => row.id !== id));
    }
  };


  // 수정?
  const processRowUpdate = (newRow) => {
    const updatedRow = { ...newRow, isNew: false };
    setRows(rows.map((row) => (row.id === newRow.id ? updatedRow : row)));
    // setRows(rows.concat(updatedRow));
    
    
    setuploadrows(uploadrows.concat(updatedRow));

    // console.log("rows",rows);
    // console.log("newRowaa",newRow);
    // console.log("uploadrows",uploadrows);
    // console.log("updatedRow",updatedRow);


    // const rorororo1 = {
    //   IDKEY:updatedRow.IDKEY
    //   ,
  
    // }

    const jsonRorororo = JSON.stringify(updatedRow);
    // console.log("왼쪽 전체수정",jsonRorororo);
    editrow(jsonRorororo);

    return updatedRow;
  };

  // 왼쪽 전체 수정사항 있는 로우를 매개변수로
  // api 호출
  const editrow = async (updatedRow) => {
    try{
      const formData = new FormData();
      formData.append('item', updatedRow);

      const response = await axios.post(`http://115.68.193.117:9999/net/data-change`, formData);

      // console.log("editing - response",response);
    }catch (error) {
      console.error('Error editing file:', error);
    }
  };

  const handleRowModesModelChange = (newRowModesModel) => {
    setRowModesModel(newRowModesModel);
  };

  const columns = apicolumns 
  ? apicolumns.map((columnName, index) => ({
      field: columnName,
      headerName: columnName === 'id' ? 'ID' : columnName,
      width: columnName === 'id' ? 350: 180 && columnName === 'question_text' ? 310 : 180 ,
      editable: true,
      ...(columnName === 'emotion'
        ? {
            type: 'singleSelect',
            valueOptions: ['긍정', '부정', '알수없음'],
          }
        : {}),
      ...(columnName === 'net_text'
        ? {
            type: 'singleSelect',
            valueOptions: net,
          }
        : {}),

      
    }))
  : [];

  // 기본 작업 열 (actions) 추가
  columns.push({
    field: 'actions',
    type: 'actions',
    headerName: 'Actions',
    width: 100,
    cellClassName: 'actions',
    getActions: ({ id }) => {
      const isInEditMode = rowModesModel[id]?.mode === GridRowModes.Edit;

      if (isInEditMode) {
        return [
          <GridActionsCellItem
            icon={<SaveIcon />}
            label="Save"
            sx={{
              color: 'primary.main',
            }}
            onClick={handleSaveClick(id)}
          />,
          <GridActionsCellItem
            icon={<CancelIcon />}
            label="Cancel"
            className="textPrimary"
            onClick={handleCancelClick(id)}
            color="inherit"
          />,
        ];
      }

      return [
        <GridActionsCellItem
          icon={<EditIcon />}
          label="Edit"
          className="textPrimary"
          onClick={handleEditClick(id)}
          color="inherit"
        />,
        // <GridActionsCellItem
        //   icon={<DeleteIcon />}
        //   label="Delete"
        //   onClick={handleDeleteClick(id)}
        //   color="inherit"
        // ee/>,
      ];
    },
  });

  return (
    <div>
      <Box
        sx={{
          height: 660,
          width: '100%',
          '& .actions': {
            color: 'text.secondary',
          },
          '& .textPrimary': {
            color: 'text.primary',
          },
        }}
      >
        <DataGrid
          rows={rows}
          columns={columns}
          editMode="row"
          rowModesModel={rowModesModel}
          onRowModesModelChange={handleRowModesModelChange}
          onRowEditStop={handleRowEditStop}
          processRowUpdate={processRowUpdate}
          slots={{
            toolbar: EditToolbar,
          }}
          slotProps={{
            toolbar: { setRows, setRowModesModel },
          }}
          onProcessRowUpdateError={(error) => {
            console.error('Error updating row:', error);
            // 추가적인 오류 처리 로직을 여기에 추가할 수 있습니다.
          }}
        />
      </Box>
    </div>
  );
}

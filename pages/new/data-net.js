import React, { use, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Side_bar from "../../newcomp/side_bar";
import Top_select from "../../newcomp/select_que";
import FullFeaturedCrudGrid2 from "../../newcomp/net_edit";
import FullFeaturedCrudGrid from "../../components/test_mui_edit_new";

export default function Home() {
  const [csvstatus, setCsvStatus] = useState(true);
  const router = useRouter();

  if (router.query.data===undefined){
      router.query.data = "LG_gram_data"
  }
  const [receivedData,setreceivedData]=useState(router.query.data);

  // 모델실행버튼클릭이벤트
  const runmodel = async (selectfile) => {
    console.log("selectfilaaae",selectfile);
  };

  // 파일명변동이벤트
  const filechanged = async (selectfile) => {
    if(selectfile!=null){
      console.log("변동",selectfile.value);
      setreceivedData(selectfile.value);
    }
  };

  const [dataFromChild, setDataFromChild] = useState('notupdated');

  const handleDataFromChild = (data) => {
    // Do something with the data received from ChildComponent
    console.log('Data from Child:_이거 부모컴포넌트임', data);
    setDataFromChild(data);
  };

  useEffect(() => {

  }, [dataFromChild]);

  const i=5;
  const page=2;
  return (
    //1번 프레임 
    <div id='outter_frame1'>
      {/* 왼쪽 바 */}
      <div id ='left_bar'>
        <Side_bar index={i}/>
      </div>
      {/* 2번 프레임 */}
      <div id='outter_frame2'>
          {/* <TopLabel activeStep={activeStepVal}/> */}
          <Top_select method2={filechanged} method={runmodel} page={page} routed={receivedData}/>
          

          {/* 메인: 선택지 , 차트내용 등 */}
          <div id='main_frame'>
            {/* <AuthCheck> */}
            <div>
              <div id='rec'>
                  {/* <p>현재 설문 : {receivedData2}</p> */}
              </div>


              <div id='csvview' className='onlyflex'>
                  {/* {csvstatus && (
                      <DynamicTable data={receivedData2}/>
                  )} */}
                  {csvstatus && (
                      <>
                      <FullFeaturedCrudGrid onDataReceived={dataFromChild} file={receivedData}/>
                      <div id='netspace'>
                        <FullFeaturedCrudGrid2 onDataReceived={setDataFromChild} file={receivedData}/>
                      </div>
                      </>
                  )}
              </div>
            </div>
            {/* </AuthCheck> */}
            {/* 메인: 선택지 , 차트내용 등 */}              
          </div>
      </div>
    </div>
  );
}

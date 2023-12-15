import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Side_bar from '../../newcomp/global_side_bar';
import Top_select from '../../newcomp/global_select_que_dash';
import PieAnimation from '../../newcomp/chart_pie';
import CombinedChart from '../../newcomp/chart_bar_line';
import AuthCheck from '../../newcomp/login_auth-check';

export default function Home() {
  const router = useRouter();

  const [receivedData, setReceivedData] = useState(router.query.p_name);
  const [receivedDataque, setReceivedDataque] = useState(router.query.question);
  const [good, setGood] = useState('bad');

  const fileChanged = async (selectfile, selectque) => {
    if (selectfile != null) {
      setReceivedData(selectfile);
      setReceivedDataque(selectque);
      setGood('good');
    }
  };

  const i = 4;
  const page = 2;

  return (
    <div id="outter_frame1">
      <div id="left_bar">
        <Side_bar index={i} />
      </div>
      <div id="outter_frame2">
        <Top_select method2={fileChanged} page={page} routed_p={receivedData} routed_q={receivedDataque} />
        <div id="main_frame">
          <AuthCheck>
            <div className="onlyflex" id="chart_contain">
              {good === 'good' && (
                <>
                  <div id="chart_pie">
                    <PieAnimation file={receivedData} fileque={receivedDataque} />
                  </div>
                  <div id="chart_bars">
                    <CombinedChart file={receivedData} fileque={receivedDataque} />
                  </div>
                </>
              )}
            </div>
          </AuthCheck>
        </div>
      </div>
    </div>
  );
}

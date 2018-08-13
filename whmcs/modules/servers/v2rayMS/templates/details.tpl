<!-- CSS -->
<link rel="stylesheet" href="modules/servers/V2rayMS/templates/static/css/style.css">
<div class="plugin">
    <div class="row">
        <div class="col-md-12">
            <!--widget start-->

                <section class="panel">
                    <ul class="nav nav-pills nav-stacked">
                        <li><a href="javascript:;"> <i class="fa fa-calendar-check"></i> {$LANG.clientareahostingregdate} : {$regdate} </a></li>
                        <li><a href="javascript:;"> <i class="fa fa-list-alt"></i> {$LANG.orderproduct} : {$groupname} - {$product} </a></li>
                        <li><a href="javascript:;"> <i class="fa fa-money-check"></i> {$LANG.orderpaymentmethod} : {$paymentmethod} {$LANG.firstpaymentamount}({$firstpaymentamount}) - {$LANG.recurringamount}({$recurringamount})</a></li>
                        <li><a href="javascript:;"> <i class="fa fa-spinner"></i> {$LANG.clientareahostingnextduedate} : {$nextduedate} {$LANG.orderbillingcycle}({$billingcycle}) </a></li>
                        <li><a href="javascript:;"> <i class="fa fa-check-square"></i> {$LANG.clientareastatus} : {$status} </a></li>
                    </ul>
                </section>

            <!--widget end-->
            <section class="panel">
                <header class="panel-heading">
                    用户信息
                </header>
                <div class="panel-body" style="padding-left:0px;">
                    <table class="table general-table">
                        <thead>
                            <tr>
                                <th>UUID(ID)</th>
                                <th>创建时间</th>
                                <th class="hidden-sm hidden-xs">上次使用</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{$usage.uuid}</td>
                                <td>{$usage.created_at|date_format:'%Y-%m-%d %H:%M:%S'}</td>
                                <td class="hidden-sm hidden-xs">{$usage.t|date_format:'%Y-%m-%d %H:%M:%S'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
            <!--progress bar start-->
            <section class="panel">
                <header class="panel-heading">
                    流量统计
                </header>
                <div class="panel-body" id="plugin-usage">
                    <p>总流量：{$usage.transfer_enable/1048576} MB &nbsp;&nbsp;&nbsp;已用流量：{($usage.sum/1048576)|round} MB &nbsp;&nbsp;&nbsp;剩余流量：{(($usage.transfer_enable/1048576)-($usage.sum/1048576))|round} MB </p>
                    <div class="progress progress-striped progress-sm">
                        <div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="{($usage.sum/$usage.transfer_enable)*100}" aria-valuemin="0" aria-valuemax="100" style="width: {($usage.sum/$usage.transfer_enable)*100}%">
                            <span class="sr-only">{($usage.sum/$usage.transfer_enable)*100}% Complete</span>
                        </div>
                    </div>
                </div>
            </section>
            <!--progress bar end-->
            <section class="panel">
                <header class="panel-heading">
                    节点列表
                </header>
                <div class="panel-body" style="padding-left:0px;">
                    <table class="table table-hover general-table">
                        <thead>
                            <tr>
                                <th >描述</th>
                                <th >地址</th>
                                <th class="hidden-sm hidden-xs">端口</th>
                                <th class="hidden-sm hidden-xs">AlterID</th>
                                <th class="hidden-sm hidden-xs">传输协议</th>
                                <th class="hidden-sm hidden-xs">伪装类型</th>
                                <th >自动配置</th>
                            </tr>
                        </thead>
                        <tbody>
                            {foreach from=$nodes key=k item=node }
                            <tr>
                                <td>{$node[0]}</td>
                                <td>{$node[1]}</td>
                                <td class="hidden-sm hidden-xs">{$node[2]}</td>
                                <td class="hidden-sm hidden-xs">{$node[3]}</td>
                                <td class="hidden-sm hidden-xs">{$node[4]}</td>
                                <td class="hidden-sm hidden-xs">{$node[5]}</td>
                                <td data-hook="action">
                                    <button name="qrcode" class="btn btn-primary btn-xs" data-type="vmess" data-params="{$node[1]|trim}:{$node[2]|trim}:{$usage.uuid|trim}:{$node[3]|trim}:{$node[4]|trim}:{$node[5]|trim}">
                                        <i class="fa fa-qrcode"></i>
                                        二维码
                                    </button>
                                </td>
                            </tr>
                            {/foreach}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    </div>
</div>
<!-- JavsScript -->
<script src="modules/servers/V2rayMS/templates/static/js/layer/layer.js"></script>
<script src="modules/servers/V2rayMS/templates/static/js/script.js"></script>
